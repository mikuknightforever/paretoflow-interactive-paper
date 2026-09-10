"""Small, independently embedded views of the same recorded experiment."""
import numpy as np
import plotly.graph_objects as go
from dash import Dash, ClientsideFunction, Input, Output, State, dcc, html, no_update
from flask import redirect
from model import DATA, MODES, COLORS, HV, nondominated

CONFIG = {'displayModeBar': False, 'responsive': True}
FINAL = DATA['guided_y'][-1]
FRONT = nondominated(FINAL)
ERROR = {m:np.abs(DATA[m+'_pred']-DATA[m+'_y']).mean(axis=(1,2)) for m in MODES}
# Load recorded coordinates once. Playback never reopens the compressed archive.
_evolution_y = DATA['guided_y']
EVOLUTION = {
    'frames': [{'x': y[:,0].tolist(), 'y': y[:,1].tolist()} for y in _evolution_y],
    'times': DATA['guided_times'].tolist(),
    'coverage': HV['guided'].tolist(),
}


def heading(number,title):
    return html.Div([html.Div([html.Span(number,className='mini-number'),html.Strong(title)]),
                     html.A('Full explorer ↗',href='/explorer',target='_blank')],className='mini-heading')


def compact(fig,height=290):
    fig.update_layout(height=height,margin=dict(l=48,r=14,t=32,b=42),
                      legend=dict(orientation='h',y=1.16,font=dict(size=11)),
                      font=dict(size=12),dragmode='pan')
    return fig


def notes(text):
    return html.Details([html.Summary('About this view'),html.P(text)],className='mini-notes')


def evolution_view(step,style):
    """Initial SVG figure; subsequent frames are applied locally by playback.js."""
    step=int(step)
    if not 0<=step<len(EVOLUTION['frames']):
        raise ValueError('Invalid recorded step')
    a=np.linspace(0,1,180)
    frame=EVOLUTION['frames'][step]
    fig=go.Figure([
        go.Scatter(x=a,y=1-a*a,name='Analytic front',mode='lines',line=dict(color='#182f44',width=2,dash='dash'),hoverinfo='skip'),
        go.Scatter(x=frame['x'],y=frame['y'],customdata=list(range(400)),mode='markers',name='Current archive',
                   marker=dict(size=7,color=np.arange(400)/399,colorscale=[[0,'#007f87'],[.5,'#347ac2'],[1,'#aa69a4']],opacity=.8),
                   hovertemplate='Direction %{customdata}<br>f₁ = %{x:.4f}<br>f₂ = %{y:.4f}<extra></extra>')
    ])
    fig.update_xaxes(title='Objective f₁',range=[-.03,1.04])
    fig.update_yaxes(title='Objective f₂',range=[-.15,9.2])
    fig.update_layout(uirevision='evolution',transition=dict(duration=0))
    t=EVOLUTION['times'][step]
    stage='Archive unchanged during flow transport' if t<.8 else 'Proposal and archive updates'
    return compact(style(fig,275),275),f't = {t:.3f} · evaluated hypervolume {EVOLUTION["coverage"][step]:.3f} · {stage}'


def make_panels(server,render,style):
    panels = {}
    for name in ('frontier','design','evolution','ablation'):
        panels[name] = Dash('pareto_'+name, server=server, url_base_pathname=f'/{name}/',
                            assets_folder='assets',title=f'ParetoFlow · {name}')
        server.add_url_rule('/'+name,endpoint='redirect_'+name,view_func=lambda name=name:redirect('/'+name+'/'))

    frontier=panels['frontier']
    frontier.layout=html.Div([
        heading('01','Which candidates offer a trade-off?'),
        html.Div([dcc.Checklist(id='front-only',options=[{'label':'Show non-dominated candidates only','value':'front'}],value=[],inline=True)],className='mini-controls'),
        dcc.Graph(id='front-plot',config=CONFIG),html.Div(id='front-detail',className='mini-readout',role='status'),
        notes('Final guided-run archive. Both objectives are minimized. Dominance is calculated against all 400 archive slots, including points hidden by the filter. The dashed curve is the analytic front.')
    ],className='mini-panel')

    @frontier.callback(Output('front-plot','figure'),Output('front-detail','children'),Input('front-only','value'),Input('front-plot','clickData'))
    def show_frontier(options,click):
        i=200
        if click and click['points'][0].get('customdata') is not None:
            i=int(click['points'][0]['customdata'])
        if not 0<=i<400:
            i=200
        if 'front' in options and not FRONT[i]:
            i=int(np.flatnonzero(FRONT)[0])
        fig=render('guided',160,'truth',[i],['front'])[0]
        trace=fig.data[-1]
        mask=FRONT if 'front' in options else np.ones(400,dtype=bool)
        indices=np.flatnonzero(mask)
        trace.x=FINAL[mask,0]; trace.y=FINAL[mask,1]; trace.customdata=indices
        trace.marker.color=indices/399
        trace.selectedpoints=[int(np.flatnonzero(indices==i)[0])]
        count=int(np.sum(np.all(FINAL<=FINAL[i],axis=1)&np.any(FINAL<FINAL[i],axis=1)))
        status='Non-dominated in this archive' if count==0 else f'Dominated by {count} archive slots'
        return compact(fig),f'Direction {i:03d} · f₁ {FINAL[i,0]:.3f} · f₂ {FINAL[i,1]:.3f} · {status}'

    design=panels['design']
    design.layout=html.Div([
        heading('02','Connect an objective point to its design'),
        html.Div([html.Label('Reference direction',htmlFor='design-choice'),dcc.Dropdown(id='design-choice',options=[{'label':f'{i:03d}','value':i} for i in range(400)],value=200,clearable=False)],className='mini-controls mini-choice'),
        html.Div([dcc.Graph(id='design-cloud',config=CONFIG),dcc.Graph(id='design-variables',config=CONFIG)],className='mini-linked'),
        html.Div(id='design-detail',className='mini-readout',role='status'),
        notes('Click the left plot or choose a direction. The right plot shows its 30 original design variables, each bounded by [0,1]. This view fixes the run and sampling time to the final guided archive.')
    ],className='mini-panel mini-design')

    @design.callback(Output('design-choice','value'),Input('design-cloud','clickData'),prevent_initial_call=True)
    def choose_design(click):
        if not click or click['points'][0].get('customdata') is None:
            return no_update
        i=int(click['points'][0]['customdata'])
        return i if 0<=i<400 else no_update

    @design.callback(Output('design-cloud','figure'),Output('design-variables','figure'),Output('design-detail','children'),Input('design-choice','value'))
    def show_design(i):
        i=int(i)
        if not 0<=i<400:
            raise ValueError('Invalid direction')
        figs=render('guided',160,'truth',[i],[])
        cloud,variables=compact(figs[0]),compact(figs[1])
        cloud.update_layout(showlegend=False)
        x=DATA['guided_x'][-1,i]
        return cloud,variables,f'Direction {i:03d} · evaluated f₁ {FINAL[i,0]:.3f}, f₂ {FINAL[i,1]:.3f} · mean of x₂…x₃₀: {x[1:].mean():.3f}'

    evolution=panels['evolution']
    initial_figure,initial_detail=evolution_view(160,style)
    evolution.layout=html.Div([
        heading('03','Watch the candidate archive change'),
        dcc.Store(id='evo-records',data=EVOLUTION),
        dcc.Interval(id='evo-clock',interval=300,disabled=True),
        dcc.Graph(id='evo-plot',figure=initial_figure,config=CONFIG),
        html.Div([html.Button('▶ Replay updates',id='evo-play',n_clicks=0),html.Div(dcc.Slider(id='evo-step',min=0,max=160,step=1,value=160,marks={0:'0',128:'0.8',160:'1.0'}),className='mini-slider')],className='mini-controls'),
        html.Div(initial_detail,id='evo-detail',className='mini-readout',role='status'),
        notes('Guided run only. Each frame is a recorded incumbent archive, not an interpolated particle trajectory. Before t=0.8 the displayed archive is unchanged. Replay skips this unchanged prefix and begins at t=0.775; the slider still exposes every earlier record. Pause stops on the current frame; Resume continues from it.')
    ],className='mini-panel')

    evolution.clientside_callback(
        ClientsideFunction(namespace='paretoPlayback',function_name='control'),
        Output('evo-clock','disabled'),Output('evo-play','children'),Output('evo-step','value'),
        Input('evo-play','n_clicks'),Input('evo-clock','n_intervals'),
        State('evo-clock','disabled'),State('evo-step','value'),prevent_initial_call=True)

    evolution.clientside_callback(
        ClientsideFunction(namespace='paretoPlayback',function_name='frame'),
        Output('evo-plot','figure'),Output('evo-detail','children'),Input('evo-step','value'),
        State('evo-records','data'),State('evo-plot','figure'),prevent_initial_call=True)

    ablation=panels['ablation']
    ablation.layout=html.Div([
        heading('04','Compare the contribution of each component'),
        html.Div([dcc.Dropdown(id='ablation-mode',options=[{'label':v,'value':k} for k,v in MODES.items()],value='guided',clearable=False),
                  dcc.RadioItems(id='ablation-metric',options=[{'label':'Coverage','value':'hv'},{'label':'Proxy error','value':'error'}],value='hv',inline=True)],className='mini-controls mini-ablation-controls'),
        dcc.Graph(id='ablation-plot',config=CONFIG),html.Div(id='ablation-detail',className='mini-readout',role='status'),
        notes('One seed, shared trained models. Coverage is analytic hypervolume with reference (1.1,10); proxy error is mean absolute error over both objective values and all archive slots, in original units. Removing gradient guidance retains the other sampling steps; removing neighbor exchange uses K=1.')
    ],className='mini-panel')

    @ablation.callback(Output('ablation-plot','figure'),Output('ablation-detail','children'),Input('ablation-mode','value'),Input('ablation-metric','value'))
    def show_ablation(mode,metric):
        if mode not in MODES or metric not in ('hv','error'):
            raise ValueError('Invalid comparison')
        values=HV if metric=='hv' else ERROR
        fig=go.Figure()
        for m,label in MODES.items():
            fig.add_trace(go.Scatter(x=DATA[m+'_times'],y=values[m],name=label,mode='lines',line=dict(color=COLORS[m],width=3 if mode==m else 1.5,shape='hv'),opacity=1 if mode==m else .55))
        fig.update_xaxes(title='Sampling time t',range=[0,1])
        fig.update_yaxes(title='Hypervolume ↑' if metric=='hv' else 'Mean absolute proxy error ↓')
        fig=compact(style(fig,290))
        fig.update_layout(margin=dict(l=58,r=14,t=68,b=42),legend=dict(y=1.35))
        return fig,f'{MODES[mode]} · final {"hypervolume" if metric=="hv" else "proxy MAE"}: {values[mode][-1]:.4f} · one recorded seed'

    # Named functions are retained for numerical/callback verification.
    for panel,fn in [(frontier,show_frontier),(design,show_design),(evolution,lambda step:evolution_view(step,style)),(ablation,show_ablation)]:
        panel.panel_render=fn
    return panels
