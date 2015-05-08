'''
Created on Apr 25, 2015

@author: brian
'''

from traitsui.api import View, Item, EnumEditor, Controller
from envisage.api import Plugin, contributes_to
from traits.api import provides, DelegatesTo, Callable
from cytoflowgui.op_plugins import IOperationPlugin, OpHandlerMixin, OP_PLUGIN_EXT
from cytoflow import Range2DOp, ScatterplotView, RangeSelection2D
from pyface.api import ImageResource
from cytoflowgui.view_plugins.i_view_plugin import ViewHandlerMixin
from cytoflowgui.subset_editor import SubsetEditor
from cytoflow.views.i_selectionview import ISelectionView

class Range2DHandler(Controller, OpHandlerMixin):
    
    def default_traits_view(self):
        return View(Item('object.name'),
                    Item('object.xchannel',
                         editor=EnumEditor(name='handler.previous_channels'),
                         label = "X Channel"),
                    Item('object.xlow', label = "X Low"),
                    Item('object.xhigh', label = "X High"),
                    Item('object.ychannel',
                         editor=EnumEditor(name='handler.previous_channels'),
                         label = "Y Channel"),
                    Item('object.ylow', label = "Y Low"),
                    Item('object.yhigh', label = "Y High")) 
        
class RangeView2DHandler(Controller, ViewHandlerMixin):
    def default_traits_view(self):
        return View(Item('object.name', 
                         style = 'readonly'),
                    Item('object.xchannel', 
                         label = "X Channel", 
                         style = 'readonly'),
                    Item('object.ychannel',
                         label = "Y Channel",
                         style = 'readonly'),
                    Item('_'),
                    Item('object.subset',
                         label = "Subset",
                         editor = SubsetEditor(experiment = 'handler.wi.previous.result')))

@provides(ISelectionView)
class Range2DSelectionView(RangeSelection2D):
    handler_factory = Callable(RangeView2DHandler)
    
    def __init__(self, **kwargs):
        super(Range2DSelectionView, self).__init__(**kwargs)
        
        self.view = ScatterplotView()
        
        self.add_trait('name', DelegatesTo('view'))
        self.add_trait('xchannel', DelegatesTo('view'))
        self.add_trait('ychannel', DelegatesTo('view'))
        self.add_trait('subset', DelegatesTo('view'))
        
    def is_wi_valid(self, wi):
        return (wi.previous 
                and wi.previous.result 
                and self.is_valid(wi.previous.result))
    
    def plot_wi(self, wi, pane):
        pane.plot(wi.previous.result, self) 

@provides(IOperationPlugin)
class Range2DPlugin(Plugin):
    """
    class docs
    """
    
    id = 'edu.mit.synbio.cytoflowgui.operations.range2d'
    operation_id = 'edu.mit.synbio.cytoflow.operations.range2d'

    short_name = "Range 2D"
    menu_group = "Gates"
    
    def get_operation(self):
        ret = Range2DOp()
        ret.handler_factory = Range2DHandler
        return ret
    
    def get_default_view(self, op):
        view = Range2DSelectionView()
         
        # we have to make these traits on the top-level ThresholdSelection
        # so that the change handlers get updated.
         
        op.sync_trait('xchannel', view, mutual = True)
        op.sync_trait('xlow', view, mutual = True)
        op.sync_trait('xhigh', view, mutual = True)
        op.sync_trait('ychannel', view, mutual = True)
        op.sync_trait('ylow', view, mutual = True)
        op.sync_trait('yhigh', view, mutual = True)
        op.sync_trait('name', view, mutual = True)
         
        return view
#     
    def get_icon(self):
        return ImageResource('range2d')
    
    @contributes_to(OP_PLUGIN_EXT)
    def get_plugin(self):
        return self