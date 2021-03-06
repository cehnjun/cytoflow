#!/usr/bin/env python3.4
# coding: latin-1

# (c) Massachusetts Institute of Technology 2015-2017
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''
Range Gate
----------

Draw a range gate.  To draw a new range, click-and-drag across the plot.

.. object:: Name

    The operation name.  Used to name the new metadata field that's created by 
    this module.
    
.. object:: Channel

    The name of the channel to apply the gate to.

.. object:: Low

    The low threshold of the gate.
    
.. object:: High

    The high threshold of the gate.
    
.. object:: Scale

    The scale of the axis for the interactive plot
    
.. object:: Hue facet

    Show different experimental conditions in different colors.
    
.. object:: Subset

    Show only a subset of the data.
   
.. plot::

    import cytoflow as flow
    import_op = flow.ImportOp()
    import_op.tubes = [flow.Tube(file = "Plate01/RFP_Well_A3.fcs",
                                 conditions = {'Dox' : 10.0}),
                       flow.Tube(file = "Plate01/CFP_Well_A4.fcs",
                                 conditions = {'Dox' : 1.0})]
    import_op.conditions = {'Dox' : 'float'}
    ex = import_op.apply()

    range_op = flow.RangeOp(name = 'Range',
                            channel = 'Y2-A',
                            low = 2000,
                            high = 10000)

    range_op.default_view(scale = 'log').plot(ex)

'''

from traits.api import provides, Callable, Str, Instance, DelegatesTo
from traitsui.api import View, Item, EnumEditor, Controller, VGroup, TextEditor
from envisage.api import Plugin, contributes_to
from pyface.api import ImageResource

from cytoflow.views.i_selectionview import ISelectionView
from cytoflow.operations import IOperation
from cytoflow.operations.range import RangeOp, RangeSelection

from cytoflowgui.op_plugins import IOperationPlugin, OpHandlerMixin, OP_PLUGIN_EXT, shared_op_traits
from cytoflowgui.view_plugins.i_view_plugin import ViewHandlerMixin, PluginViewMixin
from cytoflowgui.subset import SubsetListEditor
from cytoflowgui.color_text_editor import ColorTextEditor
from cytoflowgui.ext_enum_editor import ExtendableEnumEditor
from cytoflowgui.op_plugins.i_op_plugin import PluginOpMixin, PluginHelpMixin
from cytoflowgui.workflow import Changed

class RangeHandler(OpHandlerMixin, Controller):
    
    def default_traits_view(self):
        return View(Item('name',
                         editor = TextEditor(auto_set = False)),
                    Item('channel',
                         editor=EnumEditor(name='context.previous_wi.channels'),
                         label = "Channel"),
                    Item('low',
                         editor = TextEditor(auto_set = False)),
                    Item('high',
                         editor = TextEditor(auto_set = False)),
                    shared_op_traits) 
        
class RangeViewHandler(ViewHandlerMixin, Controller):
    def default_traits_view(self):
        return View(VGroup(
                    VGroup(Item('channel', 
                                label = "Channel",
                                style = "readonly"),
                           Item('scale'),
                           Item('huefacet',
                                editor=ExtendableEnumEditor(name='handler.previous_conditions_names',
                                                            extra_items = {"None" : ""}),
                                label="Color\nFacet"),
                            label = "Range Setup View",
                            show_border = False),
                    VGroup(Item('subset_list',
                                show_label = False,
                                editor = SubsetListEditor(conditions = "context.previous_wi.conditions")),
                           label = "Subset",
                           show_border = False,
                           show_labels = False),
                    Item('context.view_warning',
                         resizable = True,
                         visible_when = 'context.view_warning',
                         editor = ColorTextEditor(foreground_color = "#000000",
                                                 background_color = "#ffff99")),
                    Item('context.view_error',
                         resizable = True,
                         visible_when = 'context.view_error',
                         editor = ColorTextEditor(foreground_color = "#000000",
                                                  background_color = "#ff9191"))))

@provides(ISelectionView)
class RangeSelectionView(PluginViewMixin, RangeSelection):
    handler_factory = Callable(RangeViewHandler)
    op = Instance(IOperation, fixed = True)
    low = DelegatesTo('op', status = True)
    high = DelegatesTo('op', status = True)
    name = Str
    
    def should_plot(self, changed):
        if changed == Changed.PREV_RESULT or changed == Changed.VIEW:
            return True
        else:
            return False
    
    def plot_wi(self, wi):
        self.plot(wi.previous_wi.result)
    
    
@provides(IOperation)
class RangePluginOp(PluginOpMixin, RangeOp):
    handler_factory = Callable(RangeHandler)
    
    def default_view(self, **kwargs):
        return RangeSelectionView(op = self, **kwargs)

@provides(IOperationPlugin)
class RangePlugin(Plugin, PluginHelpMixin):
    
    id = 'edu.mit.synbio.cytoflowgui.op_plugins.range'
    operation_id = 'edu.mit.synbio.cytoflow.operations.range'

    short_name = "Range"
    menu_group = "Gates"
    
    def get_operation(self):
        return RangePluginOp()
    
    def get_icon(self):
        return ImageResource('range')
    
    @contributes_to(OP_PLUGIN_EXT)
    def get_plugin(self):
        return self
    