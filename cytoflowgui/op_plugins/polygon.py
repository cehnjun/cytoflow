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
Polygon Gate
------------

Draw a polygon gate.  To add vertices, use a single-click; to close the
polygon, double-click.

.. object:: Name

    The operation name.  Used to name the new metadata field that's created by 
    this module.
    
.. object:: X Channel

    The name of the channel on the gate's X axis.

.. object:: Y Channel

    The name of the channel on the gate's Y axis.
    
.. object:: X Scale

    The scale of the X axis for the interactive plot.
    
.. object:: Y Scale

    The scale of the Y axis for the interactive plot
    
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

    p = flow.PolygonOp(name = "Polygon",
                       xchannel = "V2-A",
                       ychannel = "Y2-A")
    p.vertices = [(23.411982294776319, 5158.7027015021222), 
                  (102.22182270573683, 23124.058843387455), 
                  (510.94519955277201, 23124.058843387455), 
                  (1089.5215641232173, 3800.3424832180476), 
                  (340.56382570202402, 801.98947404942271), 
                  (65.42597937575897, 1119.3133482602157)]

    p.default_view(huefacet = "Dox",
                   xscale = 'log',
                   yscale = 'log').plot(ex)

'''

from traits.api import provides, Callable, Str, Instance, DelegatesTo
from traitsui.api import View, Item, EnumEditor, Controller, VGroup, TextEditor
from envisage.api import Plugin, contributes_to
from pyface.api import ImageResource

from cytoflow.operations import IOperation
from cytoflow.views.i_selectionview import ISelectionView
from cytoflow.operations.polygon import PolygonOp, PolygonSelection

from cytoflowgui.op_plugins import IOperationPlugin, OpHandlerMixin, OP_PLUGIN_EXT, shared_op_traits
from cytoflowgui.view_plugins.i_view_plugin import ViewHandlerMixin, PluginViewMixin
from cytoflowgui.subset import SubsetListEditor
from cytoflowgui.color_text_editor import ColorTextEditor
from cytoflowgui.ext_enum_editor import ExtendableEnumEditor
from cytoflowgui.op_plugins.i_op_plugin import PluginOpMixin, PluginHelpMixin
from cytoflowgui.workflow import Changed

class PolygonHandler(OpHandlerMixin, Controller):
    def default_traits_view(self):
        return View(Item('name',
                         editor = TextEditor(auto_set = False)),
                    Item('xchannel',
                         editor=EnumEditor(name='context.previous_wi.channels'),
                         label = "X Channel"),
                    Item('ychannel',
                         editor=EnumEditor(name='context.previous_wi.channels'),
                         label = "Y Channel"),
                    shared_op_traits) 
        
class PolygonViewHandler(ViewHandlerMixin, Controller):
    def default_traits_view(self):
        return View(VGroup(
                    VGroup(Item('xchannel', 
                                label = "X Channel", 
                                style = 'readonly'),
                           Item('xscale',
                                label = "X Scale"),
                           Item('ychannel',
                                label = "Y Channel",
                                style = 'readonly'),
                           Item('yscale',
                                label = "Y Scale"),
                           Item('huefacet',
                                editor=ExtendableEnumEditor(name='handler.previous_conditions_names',
                                                            extra_items = {"None" : ""}),
                                label="Color\nFacet"),
                           label = "Polygon Setup View",
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
class PolygonSelectionView(PluginViewMixin, PolygonSelection):
    handler_factory = Callable(PolygonViewHandler)
    op = Instance(IOperation, fixed = True)
    vertices = DelegatesTo('op', status = True)
    name = Str
    
    def should_plot(self, changed):
        if changed == Changed.PREV_RESULT or changed == Changed.VIEW:
            return True
        else:
            return False
    
    def plot_wi(self, wi):
        self.plot(wi.previous_wi.result)
    
class PolygonPluginOp(PluginOpMixin, PolygonOp):
    handler_factory = Callable(PolygonHandler)
    
    def default_view(self, **kwargs):
        return PolygonSelectionView(op = self, **kwargs)

@provides(IOperationPlugin)
class PolygonPlugin(Plugin, PluginHelpMixin):
    
    id = 'edu.mit.synbio.cytoflowgui.op_plugins.polygon'
    operation_id = 'edu.mit.synbio.cytoflow.operations.polygon'

    short_name = "Polygon Gate"
    menu_group = "Gates"
    
    def get_operation(self):
        return PolygonPluginOp()
    
    def get_icon(self):
        return ImageResource('polygon')
    
    @contributes_to(OP_PLUGIN_EXT)
    def get_plugin(self):
        return self