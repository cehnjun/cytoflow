'''
Created on Aug 26, 2015

@author: brian
'''

from __future__ import division

from traits.api import HasStrictTraits, Str, CStr, CInt, File, Dict, Python, \
                       Instance, Int, CFloat, List
import numpy as np
from traits.has_traits import provides
from cytoflow.operations.i_operation import IOperation
from cytoflow.utility.util import cartesian
import FlowCytometryTools as fc
import math
import scipy.interpolate
import scipy.optimize
import pandas

from FlowCytometryTools.core.transforms import hlog, hlog_inv

from ..views import IView
import FlowCytometryTools

@provides(IOperation)
class BleedthroughPiecewiseOp(HasStrictTraits):
    """
    Apply bleedthrough correction to a set of fluorescence channels.
    
    To use, set up the `controls` dict with the single color controls; 
    call `estimate()` to parameterize the operation; check that the bleedthrough 
    plots look good with `default_view`(); and then `apply()` to an Experiment.
    
    Attributes
    ----------
    name : Str
        The operation name (for UI representation.)
    
    controls : Dict(Str, File)
        The channel names to correct, and corresponding single-color control
        FCS files to estimate the correction splines with.  Must be set to
        use `estimate()`.
        
    num_knots : Int (default = 7)
        The number of internal control points to estimate, spaced log-evenly
        from 0 to the range of the channel.  Must be set to use `estimate()`.
        
    mesh_size : Int (default = 32)
        The size of each axis in the mesh used to interpolate corrected values.
        
    Notes
    -----
    We use an interpolation-based scheme to estimate corrected bleedthrough.
    The algorithm is as follows:
     - Fit a piecewise-linear spline to each single-color control's bleedthrough
       into other channels.   
     - At each point on a regular mesh spanning the entire range of the
       instrument, estimate the mapping from (raw colors) --> (actual colors).
       This is quite slow.
     - Use these estimates to paramaterize a linear interpolator (in log space).
       There's one interpolator per output channel.  For each measured cell,
       run each interpolator to give the corrected output.
    """
    
    # traits
    id = "edu.mit.synbio.cytoflow.operations.bleedthrough_piecewise"
    friendly_id = "Piecewise Bleedthrough Correction"
    
    name = CStr()

    controls = Dict(Str, File)
    num_knots = Int(7)
    mesh_size = Int(32)

    _splines = Dict(Str, Dict(Str, Python))
    _interpolators = Dict(Str, Python)
    
    # because the order of the channels is important, we can't just call
    # _interpolators.keys()
    _channels = List(Str)
    
    def is_valid(self, experiment):
        """Validate this operation against an experiment."""

        if not self.name:
            return False
        
        # NOTE: these conditions are for applying the correction, NOT estimating
        # the correction from controls.
        
        if not self._interpolators:
            return False
        
        if not set(self._interpolators.keys()) <= set(experiment.channels):
            return False
       
        return True
    
    def estimate(self, experiment, subset = None): 
        """
        Estimate the bleedthrough from the single-channel controls in `controls`
        """

        if self.num_knots < 3:
            raise RuntimeError("Need to allow at least 3 knots in the spline")
        
        self._channels = self.controls.keys()
    
        for channel in self._channels:       
            tube = fc.FCMeasurement(ID=channel, datafile = self.controls[channel])
            
            try:
                tube.read_meta()
            except Exception:
                raise RuntimeError("FCS reader threw an error on tube {0}".format(self.controls[channel]))

            for channel in self._channels:
                exp_v = experiment.metadata[channel]['voltage']
            
                if not "$PnV" in tube.channels:
                    raise RuntimeError("Didn't find a voltage for channel {0}" \
                                       "in tube {1}".format(channel, tube.datafile))
                
                control_v = tube.channels[tube.channels['$PnN'] == channel]['$PnV'].iloc[0]
                
                if control_v != exp_v:
                    raise RuntimeError("Voltage differs for channel {0} in tube {1}"
                                       .format(channel, self.controls[channel]))

        self._splines = {}
        mesh_axes = []

        for channel in self._channels:
            self._splines[channel] = {}
            
            tube = fc.FCMeasurement(ID=channel, datafile = self.controls[channel])
            data = tube.data.sort(channel)

            for af_channel in self._channels:
                if 'af_median' in experiment.metadata[af_channel]:
                    data[af_channel] = data[af_channel] - \
                                    experiment.metadata[af_channel]['af_median']

            channel_min = data[channel].min()
            channel_max = data[channel].max()
            
            # we're going to set the knots and splines evenly across the hlog-
            # transformed data, so as to capture both the "linear" aspect
            # of near-0 and negative values, and the "log" aspect of large
            # values

            # parameterize the hlog transform
            r = experiment.metadata[channel]['range']  # instrument range
            d = np.log10(r)  # maximum display scale, in decades
            
            # the transition point from linear --> log scale
            # use half of the log-transformed scale as "linear".
            b = 2 ** (np.log2(r) / 2)
            
            # the splines' knots
            knot_min = channel_min
            knot_max = channel_max
            
            hlog_knot_min, hlog_knot_max = \
                hlog((knot_min, knot_max), b = b, r = r, d = d)
            hlog_knots = np.linspace(hlog_knot_min, hlog_knot_max, self.num_knots)
            knots = hlog_inv(hlog_knots, b = b, r = r, d = d)
            
            # only keep the interior knots
            knots = knots[1:-1] 
            
            # the interpolators' mesh            
            mesh_min = -3 * experiment.metadata[channel]['af_stdev']
            mesh_max = r
                
            hlog_mesh_min, hlog_mesh_max = \
                hlog((mesh_min, mesh_max), b = b, r = r, d = d)
            hlog_mesh_axis = \
                np.linspace(hlog_mesh_min, hlog_mesh_max, self.mesh_size)
            
            mesh_axis = hlog_inv(hlog_mesh_axis, b = b, r = r, d = d)
            mesh_axes.append(mesh_axis)
            
            for to_channel in self._channels:
                from_channel = channel
                if from_channel == to_channel:
                    continue
                
                self._splines[from_channel][to_channel] = \
                    scipy.interpolate.LSQUnivariateSpline(data[from_channel].values,
                                                          data[to_channel].values,
                                                          t = knots,
                                                          k = 1)
         
        
        mesh = pandas.DataFrame(cartesian(mesh_axes), 
                                columns = [x for x in self._channels])
         
        mesh_corrected = mesh.apply(_correct_bleedthrough,
                                    axis = 1,
                                    args = ([[x for x in self._channels], 
                                             self._splines]))
        
        for channel in self._channels:
            chan_values = np.reshape(mesh_corrected[channel], [len(x) for x in mesh_axes])
            self._interpolators[channel] = \
                scipy.interpolate.RegularGridInterpolator(mesh_axes, chan_values)

        # TODO - some sort of validity checking.

    def apply(self, old_experiment):
        """Applies the bleedthrough correction to an experiment.
        
        Parameters
        ----------
        experiment : Experiment
            the old_experiment to which this op is applied
            
        Returns
        -------
            a new experiment with the bleedthrough subtracted out.
        """

        new_experiment = old_experiment.clone()
        
        # get rid of data outside of the interpolators' mesh 
        # (-3 * autofluorescence sigma )
        for channel in self._channels:
            af_stdev = new_experiment.metadata[channel]['af_stdev']
            new_experiment.data = \
                new_experiment.data[new_experiment.data[channel] > -3 * af_stdev]
        
        new_experiment.data.reset_index(drop = True, inplace = True)
        
        old_data = new_experiment.data[self._channels]
        
        for channel in self._channels:
            new_experiment[channel] = self._interpolators[channel](old_data)
            
            # add the correction splines to the experiment metadata so we can 
            # correct other controls later on
            new_experiment.metadata[channel]['piecewise_bleedthrough'] = \
                (self._channels, self._interpolators[channel])

        return new_experiment
    
    def default_view(self):
        """
        Returns a diagnostic plot to see if the bleedthrough spline estimation
        is working.
        
        Returns
        -------
            IView : An IView, call plot() to see the diagnostic plots
        """
        
        if set(self.controls.keys()) != set(self._splines.keys()):
            raise "Must have both the controls and bleedthrough to plot" 
 
        channels = self.controls.keys()
        
        # make sure we can get the control tubes to plot the diagnostic
        for channel in channels:       
            tube = fc.FCMeasurement(ID=channel, datafile = self.controls[channel])
            
            try:
                tube.read_meta()
            except Exception:
                raise RuntimeError("FCS reader threw an error on tube {0}".format(self.controls[channel]))
        
        return BleedthroughPiecewiseDiagnostic(op = self)
    
# module-level "static" function (doesn't require a class instance
def _correct_bleedthrough(row, channels, splines):
    idx = {channel : idx for idx, channel in enumerate(channels)}
    
    def channel_error(x, channel):
        ret = row[channel] - x[idx[channel]]
        for from_channel in [c for c in channels if c != channel]:
            ret -= splines[from_channel][channel](x[idx[from_channel]])
        return ret
    
    def row_error(x):
        ret = [channel_error(x, channel) for channel in channels]
        return ret
    
    x_0 = row.loc[channels].convert_objects(convert_numeric = True)
    x = scipy.optimize.root(row_error, x_0)
    
    ret = row.copy()
    for idx, channel in enumerate(channels):
        ret[channel] = x.x[idx]
        
    return ret
        
@provides(IView)
class BleedthroughPiecewiseDiagnostic(HasStrictTraits):
    """
    Plots a scatterplot of each channel vs every other channel and the 
    bleedthrough spline
    
    Attributes
    ----------
    name : Str
        The instance name (for serialization, UI etc.)
    
    op : Instance(BleedthroughPiecewiseOp)
        The op whose parameters we're viewing
        
    """
    
    # traits   
    id = "edu.mit.synbio.cytoflow.view.autofluorescencediagnosticview"
    friendly_id = "Autofluorescence Diagnostic" 
    
    name = Str
    
    # TODO - why can't I use BleedthroughPiecewiseOp here?
    op = Instance(IOperation)
    
    def plot(self, experiment = None, **kwargs):
        """Plot a faceted histogram view of a channel"""
        
        import matplotlib.pyplot as plt
        
        kwargs.setdefault('histtype', 'stepfilled')
        kwargs.setdefault('alpha', 0.5)
        kwargs.setdefault('antialiased', True)
         
        plt.figure()
        
        channels = self.op._splines.keys()
        num_channels = len(channels)
        
        for from_idx, from_channel in enumerate(channels):
            for to_idx, to_channel in enumerate(channels):
                if from_idx == to_idx:
                    continue

                tube = fc.FCMeasurement(ID=from_channel, 
                                        datafile = self.op.controls[from_channel])
                                
                plt.subplot(num_channels, 
                            num_channels, 
                            from_idx + (to_idx * num_channels) + 1)
                plt.xscale('log', nonposx='mask')
                plt.yscale('log', nonposy='mask')
                plt.xlabel(from_channel)
                plt.ylabel(to_channel)
                plt.scatter(tube.data[from_channel],
                            tube.data[to_channel],
                            alpha = 0.1,
                            s = 1,
                            marker = 'o')
                
                spline = self.op._splines[from_channel][to_channel]
                xs = np.logspace(-1, math.log(tube.data[from_channel].max(), 10))
            
                plt.plot(xs, 
                         spline(xs), 
                         'g-', 
                         lw=3)

    def is_valid(self, experiment):
        """Validate this view against an experiment."""
        
        return self.op.is_valid(experiment)

    
