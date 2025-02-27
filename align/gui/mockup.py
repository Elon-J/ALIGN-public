# Run this app with `python mockup.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
try:
    from dash import html
    from dash import dcc
except ImportError:
    import dash_html_components as html
    import dash_core_components as dcc

from dash.dependencies import Input, Output

import math
import numpy as np

from collections import defaultdict

import logging

import pandas as pd

import plotly.graph_objects as go
import plotly.express as px

from ..pnr.render_placement import dump_blocks

import logging

logger = logging.getLogger(__name__)

def make_tradeoff_fig_wh(df, log=False, scale='Blugrn'):
    fig = px.scatter(
        df,
        x="width",
        y="height",
        color="ordering",
        color_continuous_scale=scale,
        size="size",
        width=800,
        height=800,
        hover_name="concrete_template_name",
        hover_data=['aspect_ratio','area'],
        opacity=0.8
    )

    area = df['area'].min()

    min_width, max_width = min(df['width']),max(df['width'])
    min_height, max_height = min(df['height']),max(df['height'])

    sweep_width = np.linspace( min_width, max_width, 101)
    sweep_height = area/sweep_width

    fig.add_trace(
        go.Scatter(
            x=sweep_width,
            y=sweep_height,
            mode='lines',
            showlegend=False
        )
    )

    if log:
        log_min = min( math.log10(min_width), math.log10(min_height)) - 0.01
        log_max = max( math.log10(max_width), math.log10(max_height)) + 0.01

        fig.update_xaxes(
            type="log",
            range=[log_min,log_max]
        )
        fig.update_yaxes(
            type="log",
            range=[log_min,log_max],
            scaleanchor='x',
            scaleratio = 1
        )
    else:
        linear_min = 0
        linear_max = max( max_width, max_height) * 1.1

        fig.update_xaxes(
            range=[linear_min,linear_max]
        )
        fig.update_yaxes(
            range=[linear_min,linear_max],
            scaleanchor='x',
            scaleratio = 1
        )


    return fig

def make_tradeoff_fig_aa(df, log=False, scale='Blugrn'):
    fig = px.scatter(
        df,
        x="aspect_ratio",
        y="area",
        color="ordering",
        color_continuous_scale=scale,
        size="size",
        width=800,
        height=800,
        hover_name="concrete_template_name",
        hover_data=['width','height']
    )

    area = df['area'].min()

    min_x, max_x = min(df['aspect_ratio']),max(df['aspect_ratio'])
    min_y, max_y = min(df['area']),max(df['area'])

    sweep_x = np.linspace( min_x, max_x, 101)
    sweep_y = area+0*sweep_x

    fig.add_trace(
        go.Scatter(
            x=sweep_x,
            y=sweep_y,
            mode='lines',
            showlegend=False
        )
    )

    if log:
        fig.update_xaxes(
            type="log"
        )
        fig.update_yaxes(
            type="log"
        )
    else:
        fig.update_xaxes(
        )
        fig.update_yaxes(
        )

    return fig

def define_axes( fig, log, max_x, max_y, *, log_one_to_one=False):
    if log:
        fig.update_xaxes(
            type="log"
        )
        if log_one_to_one:
            fig.update_yaxes(
                type="log",
                scaleanchor='x',
                scaleratio = 1
            )
        else:
            fig.update_yaxes(
                type="log"
            )
    else:
        fig.update_xaxes(
            range=[0,max_x*1.1]
        )
        fig.update_yaxes(
            range=[0,max_y*1.1]
        )


def define_colorscale( fig, col):
    min_c,max_c = col.min(),col.max()
    if min_c == max_c:
        fig.update_coloraxes(
            cmin=min_c,
            cmax=max_c,
            showscale=False
        )
    else:
        fig.update_coloraxes(
            cmin=min_c,
            cmax=max_c
        )


def make_tradeoff_fig_ha(df, log=False, scale='Blugrn', lambda_coeff=1.0):
    fig = px.scatter(
        df,
        x="hpwl",
        y="area",
        color="constraint_penalty",
        color_continuous_scale=scale,
        size="size",
        width=800,
        height=800,
        hover_name="concrete_template_name",
        hover_data=['width','height']
    )

    best_x = df['hpwl'].values[0]
    best_y = df['area'].values[0]

    min_x, max_x = min(df['hpwl']),max(df['hpwl'])
    min_y, max_y = min(df['area']),max(df['area'])

    if min_x > 0:
        log_product = math.log(best_x)*lambda_coeff + math.log(best_y)

        alt_min_x = min_x / ((max_x/min_x) ** 0.1)

        alt_min_y = min_y / ((max_y/min_y) ** 0.1)

        # find x where cost = f(x,min_y)
        alt_max_x = math.exp( (log_product - math.log(alt_min_y))/lambda_coeff)

        sweep_x = np.linspace( alt_min_x, min(alt_max_x,max_x), 101)
        log_sweep_y = log_product - np.log(sweep_x)*lambda_coeff
        sweep_y = np.exp(log_sweep_y)

        fig.add_trace(
            go.Scatter(
                x=sweep_x,
                y=sweep_y,
                mode='lines',
                showlegend=False
            )
        )

    define_colorscale( fig, df['constraint_penalty'])
    define_axes( fig, log, max_x, max_y, log_one_to_one=True)

    return fig

def make_tradeoff_fig_nn(df, log=False, scale='Blugrn'):
    fig = px.scatter(
        df,
        x="hpwl_norm",
        y="area_norm",
        color="constraint_penalty",
        color_continuous_scale=scale,
        size="size",
        width=800,
        height=800,
        hover_name="concrete_template_name",
        hover_data=['width','height']
    )

    best_x = df['hpwl_norm'].values[0]
    best_y = df['area_norm'].values[0]

    min_x, max_x = min(df['hpwl_norm']),max(df['hpwl_norm'])
    min_y, max_y = min(df['area_norm']),max(df['area_norm'])

    sweep_x = np.linspace( min_x, max_x, 101)
    sweep_y = best_y*(2 - sweep_x/best_x)

    fig.add_trace(
        go.Scatter(
            x=sweep_x,
            y=sweep_y,
            mode='lines',
            showlegend=False
        )
    )

    define_colorscale( fig, df['constraint_penalty'])
    define_axes( fig, log, max_x, max_y)

    return fig

def make_tradeoff_fig_ac(df, log=False, scale='Blugrn'):
    fig = px.scatter(
        df,
        x="area",
        y="cost",
        color="constraint_penalty",
        color_continuous_scale=scale,
        size="size",
        width=800,
        height=800,
        hover_name="concrete_template_name",
        hover_data=['width','height']
    )

    y = df['cost'].min()

    min_x, max_x = min(df['area']),max(df['area'])
    min_y, max_y = min(df['cost']),max(df['cost'])

    sweep_x = np.linspace( min_x, max_x, 101)
    sweep_y = y+0*sweep_x

    fig.add_trace(
        go.Scatter(
            x=sweep_x,
            y=sweep_y,
            mode='lines',
            showlegend=False
        )
    )

    define_colorscale( fig, df['constraint_penalty'])
    define_axes( fig, log, max_x, max_y)

    return fig




def make_tradeoff_fig_hc(df, log=False, scale='Blugrn'):
    fig = px.scatter(
        df,
        x="hpwl",
        y="cost",
        color="constraint_penalty",
        color_continuous_scale=scale,
        size="size",
        width=800,
        height=800,
        hover_name="concrete_template_name",
        hover_data=['width','height']
    )

    y = df['cost'].min()

    min_x, max_x = min(df['hpwl']),max(df['hpwl'])
    min_y, max_y = min(df['cost']),max(df['cost'])

    sweep_x = np.linspace( min_x, max_x, 101)
    sweep_y = y+0*sweep_x

    fig.add_trace(
        go.Scatter(
            x=sweep_x,
            y=sweep_y,
            mode='lines',
            showlegend=False
        )
    )

    define_colorscale( fig, df['constraint_penalty'])
    define_axes( fig, log, max_x, max_y)

    return fig

def make_tradeoff_fig( axes, df, log=False, scale='Blugrn', lambda_coeff=1.0):
    if   axes == ('width', 'height'):
        return make_tradeoff_fig_wh( df, log, scale)
    elif axes == ('aspect_ratio', 'area'):
        return make_tradeoff_fig_aa( df, log, scale)
    elif axes == ('hpwl', 'area'):
        return make_tradeoff_fig_ha( df, log, scale, lambda_coeff)
    elif axes == ('area', 'cost'):
        return make_tradeoff_fig_ac( df, log, scale)
    elif axes == ('hpwl', 'cost'):
        return make_tradeoff_fig_hc( df, log, scale)
    elif axes == ('hpwl_norm', 'area_norm'):
        return make_tradeoff_fig_nn( df, log, scale)
    else:
        assert False, axes

colorscales = ['Blugrn'] + px.colors.named_colorscales()

class AppWithCallbacksAndState:
    def gen_dataframe( self):
        data = [ { 'abstract_template_name': atn, 'concrete_template_name': ctn, **m} for atn, v in self.tagged_bboxes.items() for ctn, (m, _, _) in v.items()]

        df = pd.DataFrame( data=data)
        df['area'] = df['width']*df['height']
        df['aspect_ratio'] = df['height'] / df['width']

        self.tagged_histos = {}
        for atn, df_group0 in df.groupby(['abstract_template_name']):
            self.tagged_histos[atn] = defaultdict(list)
            for p, df_group1 in df_group0.groupby(list(self.axes)):
                for row_index, row in df_group1.iterrows():
                    self.tagged_histos[atn][p].append( row['concrete_template_name'])

        df = df[df['abstract_template_name'] == self.module_name]
        df['ordering'] = np.arange(len(df))
        df['size'] = len(df) - np.arange(len(df))

        self.df = df

    def __init__(self, *, tagged_bboxes, module_name, lambda_coeff):
        self.tagged_bboxes = tagged_bboxes
        self.module_name = module_name
        self.lambda_coeff = lambda_coeff

        self.nets_d = None

        self.sel = f'{module_name}_0'
        self.title = None

        self.subindex = 0
        self.prev_idx = None

        self.axes = ('hpwl', 'area')

        self.gen_dataframe()
        self.tradeoff = make_tradeoff_fig(self.axes, self.df, log=True, lambda_coeff=lambda_coeff)
        self.make_placement_graph()

        self.app = dash.Dash(__name__, assets_ignore=r'.*\.#.*')

        self.app.layout = html.Div(
            id='frame',
            children=[
                html.Div(
                    id='pareto-col',
                    children=[
                        html.H2(children='Pareto Frontier'),
                        dcc.RadioItems(
                            id='axes-type',
                            options=[{'label': i, 'value': i} for i in ['linear', 'loglog']],
                            value='loglog'
                        ),
                        dcc.Dropdown(
                            id='tradeoff-type',
                            options=[{"value": x, "label": x}
                                     for x in ['width-height', 'aspect_ratio-area', 'hpwl-area', 'area-cost', 'hpwl-cost', 'hpwl_norm-area_norm']],
                            value='hpwl-area'
                        ),
                        dcc.Dropdown(
                            id='colorscale',
                            options=[{"value": x, "label": x}
                                     for x in colorscales],
                            value='Blugrn'
                        ),
                        dcc.Dropdown(
                            id='module-name',
                            options=[{"value": x, "label": x}
                                     for x in self.tagged_bboxes.keys()],
                            value=self.module_name
                        ),
                        dcc.Graph(
                            id='tradeoff-graph',
                            figure=self.tradeoff
                        )
                    ]
                ),
                html.Div(
                    id='placement-col',
                    children=[
                        html.H2(children='Placement'),
                        dcc.RadioItems(
                            id='display-type',
                            options=[{'label': i, 'value': i} for i in ['All', 'Direct', 'Leaves Only']],
                            value='Direct'
                        ),
                        dcc.RadioItems(
                            id='display-pins-type',
                            options=[{'label': i, 'value': i} for i in ['No Pins', 'Pins']],
                            value='Pins'
                        ),
                        dcc.Dropdown(
                            id='netname',
                            options=[],
                            multi=True,
                            value=[]
                        ),
                        dcc.Graph(
                            id='Placement',
                            figure = self.placement_graph
                        )
                    ]
                ),
                html.Div(
                    id='tree-col',
                    children=[
                        html.Img(src=self.app.get_asset_url('align.png'))
                    ]
                )
            ]
        )

        self.app.callback( (Output('Placement', 'figure'),
                            Output('tradeoff-graph', 'clickData'),
                            Output('netname', 'options')),
                      [Input('tradeoff-graph', 'clickData'),
                       Input('tradeoff-graph', 'hoverData'),
                       Input('display-type', 'value'),
                       Input('display-pins-type', 'value'),
                       Input('netname', 'value')])(self.display_hover_data)

        self.app.callback( (Output('tradeoff-graph', 'figure'),),
                           [Input('colorscale', 'value'),
                            Input('tradeoff-type', 'value'),
                            Input('axes-type', 'value'),
                            Input('module-name', 'value')])(self.change_colorscale)

    def make_placement_graph( self, *, display_type='Direct', display_pins_type='Pins', netname=None):
        sel = self.sel
        title = self.title

        if display_type == 'All':
            levels = None
            leaves_only = False
        elif display_type == 'Direct':
            levels = 1
            leaves_only = False
        elif display_type == 'Leaves Only':
            leaves_only = True
            levels = None
        else:
            assert False, display_type

        fig = go.Figure()
        title_d = {}

        if sel is not None:
            _, d, self.nets_d = self.tagged_bboxes[self.module_name][sel]

            if netname is not None:
                for net in netname:
                    net_tuple = tuple( net.split('/'))
                    if net_tuple not in self.nets_d:
                        print( f'Error Unknown net: {net} {list(self.nets_d.keys())}')

            dump_blocks( fig, d, leaves_only, levels, netname if display_pins_type == 'Pins' else None)
            title_d = dict(text=sel if title is None else title)

        fig.update_layout(
            autosize=False,
            width=1024,
            height=1024,
            title=title_d
        )

        max_x = max( m['width']  for _, (m, _, _) in self.tagged_bboxes[self.module_name].items())
        max_y = max( m['height'] for _, (m, _, _) in self.tagged_bboxes[self.module_name].items())

        fig.update_xaxes(
            tickvals=[0,max_x],
            range=[0,max(max_x,max_y)]
        )

        fig.update_yaxes(
            tickvals=[0,max_y],
            range=[0,max(max_x,max_y)]
        )

        self.placement_graph = fig

    def change_colorscale(self, scale, tradeoff_type, axes_type, module_name):
        # if module_name changes
        ctx = dash.callback_context
        if ctx.triggered:
            d = ctx.triggered[0]
            if d['prop_id'] == 'module-name.value':
                self.module_name = module_name
            elif d['prop_id'] == 'tradeoff-type.value':
                self.axes = tuple(tradeoff_type.split('-'))

        self.gen_dataframe()
        self.tradeoff = make_tradeoff_fig(self.axes, self.df, log=axes_type == 'loglog', scale=scale, lambda_coeff=self.lambda_coeff)
        return (self.tradeoff,)

    def display_hover_data(self,clickData,hoverData,display_type,display_pins_type,netname):
        display_type_change = False

        ctx = dash.callback_context
        if ctx.triggered:
            d = ctx.triggered[0]
            if d['prop_id'] == 'display-type.value':
                display_type_change = True
            if d['prop_id'] == 'display-pins-type.value':
                display_type_change = True
            if d['prop_id'] == 'netname.value':
                display_type_change = True
            if d['prop_id'] == 'tradeoff-graph.clickData':
                pass
            if d['prop_id'] == 'tradeoff-graph.hoverData':
                pass

        if clickData is not None:
            [idx, curve_idx, x, y] = [clickData['points'][0][t] for t in ['pointNumber', 'curveNumber', 'x', 'y']]

        if hoverData is not None:
            [idx, curve_idx, x, y] = [hoverData['points'][0][t] for t in ['pointNumber', 'curveNumber', 'x', 'y']]

        if display_type_change:
            self.make_placement_graph(display_type=display_type,display_pins_type=display_pins_type,netname=netname)
        elif (clickData is not None or hoverData is not None) and \
             curve_idx == 0:

            lst = self.tagged_histos[self.module_name][(x,y)]

            if self.prev_idx != idx:
                self.subindex = 0
            else:
                self.subindex = (self.subindex+1)%len(lst)
            self.sel = lst[self.subindex]
            self.prev_idx = idx

            self.title = f'{self.sel} {self.subindex}/{len(lst)}'

            self.make_placement_graph(display_type=display_type,display_pins_type=display_pins_type,netname=netname)


        options = []
        if self.nets_d is not None:
            for k, v in self.nets_d.items():
                net = '/'.join(k)
                options.append( {"value": net, "label": net})

        return self.placement_graph, None, options


def run_gui( *, tagged_bboxes, module_name, lambda_coeff):
    awcas = AppWithCallbacksAndState( tagged_bboxes=tagged_bboxes, module_name=module_name, lambda_coeff=lambda_coeff)
    awcas.app.run_server(debug=True,use_reloader=False)

    logger.info( f'final selection: {awcas.sel} We have access to any state from the GUI object here.')
    return awcas.sel
