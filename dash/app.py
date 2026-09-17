import io
import os
import csv
import numpy as np
import plotly.graph_objects as go
from dash import Dash, ClientsideFunction, Input, Output, State, ctx, dcc, html, no_update
from flask import jsonify
from model import DATA, META, MODES, COLORS, HV, view, nondominated

app = Dash(__name__, title='ParetoFlow · A moving frontier')
server = app.server


def style(fig,height):
    fig.update_layout(template='plotly_white',height=height,margin=dict(l=55,r=20,t=25,b=45),
                      font=dict(family='Arial, sans-serif',size=13,color='#233648'),
                      paper_bgcolor='white',plot_bgcolor='white')
    return fig


def stat(label,value):
    return html.Div([html.Strong(value),html.Span(label)],className='stat')


app.layout = html.Div([
    dcc.Store(id='selection',data=[200]), dcc.Interval(id='clock',interval=350,disabled=True),
    html.Header([html.Div([html.Span('PARETOFLOW',className='wordmark'),html.Span(' / ZDT2 RESEARCH EXPLORER',className='submark')]),
                 html.A('Paper ↗',href='https://openreview.net/forum?id=mLyyB4le5u',target='_blank')]),
    html.Main([
        html.Div([html.Div([html.Span('RECORDED CPU EXPERIMENT',className='eyebrow'),html.H1('A moving frontier'),
                           html.P('Inspect the trade-off surface, select a candidate, and trace how its design changes during sampling.')]),
                  html.Div([html.Strong('30 → 2'),html.Span('design variables → objectives')],className='dimensions')],className='intro'),
        html.Div([
            html.Div([html.Label('Recorded configuration',htmlFor='mode'),dcc.Dropdown(id='mode',options=[{'label':v,'value':k} for k,v in MODES.items()],value='guided',clearable=False)],className='control wide'),
            html.Div([html.Label('Objective values',htmlFor='values'),dcc.RadioItems(id='values',options=[{'label':'Analytic evaluation','value':'truth'},{'label':'Proxy prediction','value':'proxy'}],value='truth',inline=True)],className='control'),
            html.Div([html.Label('Context layers'),dcc.Checklist(id='layers',options=[{'label':'Offline data','value':'offline'},{'label':'True front','value':'front'}],value=['offline','front'],inline=True)],className='control')],className='controls'),
        html.Div([html.Button('▶ Replay',id='play',n_clicks=0),html.Div([html.Div(id='time-label',className='time-label'),
                  dcc.Slider(id='step',min=0,max=160,step=1,value=160,marks={0:'0.00',80:'0.50',128:'0.80 · guidance begins',160:'1.00'},updatemode='mouseup')],className='slider')],className='timeline'),
        html.Div(id='stats',className='stats'),
        html.Div([
            html.Section([html.Div([html.H2('Objective space'),html.Span('Both objectives minimized ↙',className='hint')],className='plot-title'),
                          dcc.Graph(id='cloud',config={'displaylogo':False,'modeBarButtonsToRemove':['autoScale2d']},clear_on_unhover=True),
                          html.P('Click a colored point to inspect one direction. Use box or lasso selection to inspect a group. Gray points show a fixed 1,000-row context sample.',className='caption')],className='panel'),
            html.Section([html.Div([html.H2('Design space'),html.Button('Reset selection',id='clear',n_clicks=0,className='text-button')],className='plot-title'),
                          html.Div(id='detail',className='detail'),dcc.Graph(id='design',config={'displayModeBar':False}),
                          html.P('For a group, the line is the mean and the band is the variable range. All 30 variables are shown in their original [0,1] bounds.',className='caption')],className='panel')],className='linked'),
        html.Section([html.Div([html.H2('Evaluated coverage across sampling time'),html.Button('Download selected candidates',id='download-button',n_clicks=0,className='text-button')],className='plot-title'),
                      dcc.Graph(id='progress',config={'displayModeBar':False}),dcc.Download(id='download'),
                      html.P('Hypervolume uses analytic objective values and a fixed reference point (1.1, 10). The vertical line follows the time control; all three runs share training and sampling seeds.',className='caption')],className='panel progress'),
        html.Div([html.Strong('How to read this sample. '), 'A point is the current incumbent for a reference direction. Replacements are discrete archive updates, not a smooth particle trajectory. The playback shows stored computation; it does not interpolate toward the known front. ',
                  html.A('Source and run settings',href='/provenance',target='_blank')],className='note'),
    ]),html.Footer('Independent small-scale run using the authors’ sampler with documented correctness fixes. Not a reproduction of the paper’s benchmark tables.')
])


@app.callback(Output('selection','data'),Input('cloud','clickData'),Input('cloud','selectedData'),Input('clear','n_clicks'),State('selection','data'),prevent_initial_call=True)
def select(click,selected,clear,current):
    trigger = ctx.triggered[0]['prop_id']
    if trigger.startswith('clear.'):
        return [200]
    data = click if trigger.endswith('clickData') else selected
    if not data:
        return no_update
    ids = sorted({int(p['customdata']) for p in data['points'] if p.get('customdata') is not None and 0<=int(p['customdata'])<400})
    return ids or no_update


# Pause locally so a later tick cannot replace an in-flight server pause request.
app.clientside_callback(
    ClientsideFunction(namespace='paretoPlayback',function_name='explorerControl'),
    Output('clock','disabled'),Output('play','children'),Output('step','value'),
    Input('play','n_clicks'),Input('clock','n_intervals'),
    State('clock','disabled'),State('step','value'),prevent_initial_call=True)


@app.callback(Output('cloud','figure'),Output('design','figure'),Output('progress','figure'),Output('stats','children'),Output('detail','children'),Output('time-label','children'),
              Input('mode','value'),Input('step','value'),Input('values','value'),Input('selection','data'),Input('layers','value'))
def render(mode,step,value_mode,ids,layers):
    step=int(step)
    x,y,pred = view(mode,step,ids)
    objective = y if value_mode=='truth' else pred
    selected=np.array(ids,dtype=int)
    front=nondominated(y)
    times=DATA[mode+'_times']
    cloud=go.Figure()
    if 'offline' in layers:
        offline=DATA['offline_y'][::12]
        cloud.add_trace(go.Scattergl(x=offline[:,0],y=offline[:,1],mode='markers',name='Offline observations',customdata=np.full(len(offline),-1),marker=dict(size=4,color='#c6d0d8',opacity=.35),hoverinfo='skip'))
    if 'front' in layers:
        a=np.linspace(0,1,180)
        cloud.add_trace(go.Scatter(x=a,y=1-a*a,name='Analytic front',mode='lines',line=dict(color='#182f44',width=2,dash='dash'),hoverinfo='skip'))
    cloud.add_trace(go.Scattergl(x=objective[:,0],y=objective[:,1],customdata=np.arange(400),mode='markers',name='Current archive',
        marker=dict(size=7,color=np.arange(400)/399,colorscale=[[0,'#007f87'],[.5,'#347ac2'],[1,'#aa69a4']],opacity=.8),
        selectedpoints=ids,selected=dict(marker=dict(size=11,opacity=1)),unselected=dict(marker=dict(opacity=.45)),
        hovertemplate='Direction %{customdata}<br>f₁ = %{x:.4f}<br>f₂ = %{y:.4f}<extra></extra>'))
    if value_mode=='proxy':
        for i in ids[:12]:
            cloud.add_trace(go.Scatter(x=[pred[i,0],y[i,0]],y=[pred[i,1],y[i,1]],mode='lines+markers',line=dict(color='#dd962c',width=2),name='Prediction → evaluated',showlegend=False,hoverinfo='skip'))
    cloud.update_xaxes(title='Objective f₁',range=[-.03,1.04])
    cloud.update_yaxes(title='Objective f₂',range=[-.15,9.2])
    cloud.update_layout(dragmode='lasso',uirevision='objectives',legend=dict(orientation='h',y=1.12,font=dict(size=12)))
    design=go.Figure()
    variables=np.arange(1,31)
    if len(ids)>1:
        design.add_trace(go.Scatter(x=np.r_[variables,variables[::-1]],y=np.r_[x[selected].max(0),x[selected].min(0)[::-1]],fill='toself',fillcolor='rgba(21,106,171,.15)',line=dict(width=0),hoverinfo='skip',showlegend=False))
    design.add_trace(go.Scatter(x=variables,y=x[selected].mean(0),mode='lines+markers',line=dict(color=COLORS[mode],width=2),marker=dict(size=5),name='Current design',hovertemplate='x%{x} = %{y:.4f}<extra></extra>'))
    design.update_xaxes(title='Design variable',dtick=5,range=[.5,30.5])
    design.update_yaxes(title='Value',range=[-.04,1.04])
    design.update_layout(showlegend=False,uirevision='variables')
    progress=go.Figure()
    for m,label in MODES.items():
        progress.add_trace(go.Scatter(x=DATA[m+'_times'],y=HV[m],mode='lines',name=label,line=dict(color=COLORS[m],width=3 if m==mode else 1.5,shape='hv')))
    progress.add_vline(x=times[step],line=dict(color='#25384b',width=1,dash='dot'))
    progress.add_vrect(x0=.8,x1=1,fillcolor='#edf5f9',opacity=.7,line_width=0,layer='below')
    progress.update_xaxes(title='Sampling time t',range=[0,1])
    progress.update_yaxes(title='Hypervolume ↑')
    progress.update_layout(legend=dict(orientation='h',y=1.25,font=dict(size=12)),uirevision='coverage')
    ma=np.abs(pred[selected]-y[selected]).mean()
    stats=[stat('Archive slots',400),stat('Unique evaluated non-dominated',len(np.unique(y[front],axis=0))),stat('Evaluated hypervolume',f'{HV[mode][step]:.3f}'),stat('Selected directions',len(ids))]
    detail=[html.Strong(f'Direction {ids[0]:03d}' if len(ids)==1 else f'{len(ids)} directions selected'),
            html.Span(f"Evaluated f₁ {y[selected,0].mean():.3f} · f₂ {y[selected,1].mean():.3f}"),html.Span(f'Mean proxy error: {ma:.4f}')]
    return style(cloud,430),style(design,335),style(progress,220),stats,detail,f't = {times[step]:.3f} / 1.000 · '+('flow transport; archive unchanged' if times[step]<.8 else 'proposal and archive update')


@app.callback(Output('download','data'),Input('download-button','n_clicks'),State('mode','value'),State('step','value'),State('selection','data'),prevent_initial_call=True)
def download(n,mode,step,ids):
    x,y,pred=view(mode,int(step),ids)
    f=io.StringIO()
    w=csv.writer(f)
    w.writerow(['configuration','step','direction','evaluated_f1','evaluated_f2','predicted_f1','predicted_f2']+[f'x{i}' for i in range(1,31)])
    for i in ids:
        w.writerow([mode,step,i,*y[i],*pred[i],*x[i]])
    return {'content':f.getvalue(),'filename':f'paretoflow-{mode}-step-{step}.csv','type':'text/csv'}


@server.get('/health')
def health():
    return jsonify(status='ok',sample='ParetoFlow-ZDT2',modes=list(MODES))


@server.get('/provenance')
def provenance():
    return jsonify(META)


from panels import make_panels
PANELS = make_panels(server, render, style)
from paper_views import make_paper_panels
PAPER_PANELS = make_paper_panels(server)
from process_view import make_process_panel
PROCESS_PANEL = make_process_panel(server)


if __name__=='__main__':
    app.run(host='127.0.0.1',port=int(os.environ.get('PORT','8053')),debug=False)
