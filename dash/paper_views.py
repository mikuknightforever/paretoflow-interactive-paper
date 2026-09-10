"""Focused views of the complete paper: mechanics, published evidence, sources."""
import csv
import io
from urllib.parse import parse_qs
import numpy as np
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html, dash_table
from flask import jsonify, redirect, Response
from paper_data import PAPER, TABLES, METHODS, TASKS, cell, task_cell

PURPLE='#6950a1'
BLUE='#167b9b'
GRAY='#b5bdc9'
CONFIG={'displayModeBar':False,'responsive':True}


def chart(fig,height=290):
    fig.update_layout(template='plotly_white',height=height,
        margin=dict(l=60,r=24,t=20,b=45),paper_bgcolor='white',plot_bgcolor='white',
        font=dict(family='Arial, sans-serif',size=12,color='#24364a'),
        legend=dict(orientation='h',y=1.15,font=dict(size=11)),
        transition=dict(duration=0),dragmode=False)
    return fig


def graph(id):
    return dcc.Graph(id=id,config=CONFIG,style={'height':'290px'})


def head(title,kind,source):
    return html.Div([html.Div([html.Span(kind,className='paper-kind'),html.Strong(title)]),
        html.A('Paper ↗',href=PAPER['url']+'#'+source,target='_blank')],className='paper-heading')


def foot(text):
    return html.Div(text,className='paper-foot')


def source_note(text,table_id):
    return html.Span([text,' ',html.A('View source table ↗',href=PAPER['url']+'#'+table_id,target='_blank')])


def sorted_source_rows(key,sort_by):
    table=TABLES[key];rows=list(table['rows'])
    if not sort_by:return rows
    column=int(sort_by[0]['column_id'])
    if not 0<=column<len(table['columns']):return rows
    reverse=sort_by[0]['direction']=='desc'
    if column==0:return sorted(rows,key=lambda r:r[0].casefold(),reverse=reverse)
    available=[r for r in rows if r[column]!='N/A']
    missing=[r for r in rows if r[column]=='N/A']
    return sorted(available,key=lambda r:float(r[column].split('±')[0].strip()),reverse=reverse)+missing


def dropdown(id,options,value):
    return dcc.Dropdown(id=id,options=[{'label':label,'value':key} for key,label in options],value=value,clearable=False)


def comparisons(table_id,column,methods,axis='Published hypervolume ↑'):
    data=[(m,*cell(table_id,m,column)) for m in methods]
    valid=[r for r in data if r[1] is not None]
    fig=go.Figure(go.Bar(x=[r[1] for r in valid],y=[r[0] for r in valid],orientation='h',
        marker_color=[PURPLE if r[0].startswith('ParetoFlow') else BLUE if r[0]!='D-Best' else GRAY for r in valid],
        error_x=dict(type='data',array=[r[2] or 0 for r in valid],color='#465065',thickness=1),
        customdata=[r[3] for r in valid],hovertemplate='%{y}: %{customdata}<extra></extra>'))
    fig.update_xaxes(title=axis,rangemode='tozero')
    fig.update_yaxes(autorange='reversed',automargin=True)
    fig=chart(fig)
    fig.update_layout(margin=dict(l=135,r=24,t=10,b=45),bargap=.4)
    return fig


STEPS=[
    ('Learn from offline data','Fit one objective predictor per property and a flow velocity field on the same fixed dataset. The true evaluation oracle is reserved for assessment.', 'Algorithm 1 · lines 1–2'),
    ('Allocate trade-off directions','Create Das–Dennis weight vectors. Associate each with a sampling stream and find nearby weights by angle, including the direction itself.', 'Algorithm 1 · lines 3–4'),
    ('Initialize noise and archive','Start the streams from Gaussian noise and retain good offline designs in an incumbent archive. The noisy stream state and the saved clean design are distinct.', 'Algorithm 1 · lines 5–6'),
    ('Guide and propose','Estimate a clean endpoint, evaluate its learned objectives and add their weighted gradient to the flow velocity. Gaussian perturbations produce multiple offspring.', 'Equations 7–10 · line 14'),
    ('Pool neighboring offspring','For each direction, collect O proposals from each of its K neighboring streams: K × O candidates before filtering.', 'Equation 11 · line 16'),
    ('Filter and select','Keep predicted objective vectors inside the direction’s angular cone. Select the survivor with the best negative weighted objective score.', 'Equation 12 · lines 17–18'),
    ('Retain and return','Update an archive slot only when the predicted clean design improves its score. At the end, non-dominated sorting selects 256 designs for oracle evaluation.', 'Algorithm 1 · lines 19–21')]


def method_view(step):
    step=int(step)
    title,body,source=STEPS[step]
    xs=[0,1,2,3,4,5,6]
    labels=['Train','Weights','Initialize','Propose','Neighbors','Filter','Archive']
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=xs,y=[0]*7,mode='lines',line=dict(color='#d6deea',width=3),hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=xs,y=[0]*7,mode='markers+text',text=[str(i+1) for i in xs],textposition='middle center',
        textfont=dict(color='white',size=14),marker=dict(size=32,color=[PURPLE if i==step else '#9faebe' for i in xs]),hoverinfo='skip'))
    for i,label in enumerate(labels):
        fig.add_annotation(x=i,y=-.26,text=label,showarrow=False,font=dict(size=11))
    fig.add_annotation(x=3,y=.5,text='Fixed training → one sampling step → retained evidence',showarrow=False,font=dict(size=13,color='#5e6b7e'))
    fig.update_xaxes(visible=False,range=[-.35,6.35],fixedrange=True)
    fig.update_yaxes(visible=False,range=[-.6,.7],fixedrange=True)
    fig=chart(fig,170);fig.update_layout(showlegend=False,margin=dict(l=4,r=4,t=0,b=0))
    return fig,html.Div([html.Strong(title),html.P(body),html.Small(source)])


def guidance_view(shape,weight,filtering):
    w=np.array([float(weight),1-float(weight)])
    x=np.linspace(0,1,501)
    y=1-np.sqrt(x) if shape=='convex' else 1-x*x
    points=np.column_stack((x,y))
    angle=np.degrees(np.arccos(np.clip(points@w/(np.linalg.norm(points,axis=1)*np.linalg.norm(w)),-1,1)))
    keep=angle<=8 if filtering else np.ones(501,dtype=bool)
    candidates=np.flatnonzero(keep)
    winner=int(candidates[np.argmin(points[keep]@w)]) if len(candidates) else None
    theta=np.arctan2(w[1],w[0])
    fig=go.Figure(go.Scatter(x=x,y=y,mode='lines',name='Analytic reference front',line=dict(color='#748396',width=2)))
    if filtering:
        angles=np.clip([theta-np.deg2rad(8),theta+np.deg2rad(8)],0,np.pi/2)
        fig.add_trace(go.Scatter(x=[0,1.5*np.cos(angles[0]),1.5*np.cos(angles[1]),0],y=[0,1.5*np.sin(angles[0]),1.5*np.sin(angles[1]),0],
            fill='toself',fillcolor='rgba(105,80,161,.10)',line=dict(width=0),hoverinfo='skip',showlegend=False))
        fig.add_trace(go.Scatter(x=x[keep],y=y[keep],mode='lines',line=dict(color=PURPLE,width=5),name='Inside illustrative cone'))
    fig.add_trace(go.Scatter(x=[0,1.35*np.cos(theta)],y=[0,1.35*np.sin(theta)],mode='lines',line=dict(color=BLUE,dash='dot'),showlegend=False,hoverinfo='skip'))
    if winner is not None:
        fig.add_trace(go.Scatter(x=[x[winner]],y=[y[winner]],mode='markers',marker=dict(size=15,symbol='star',color=PURPLE),name='Best weighted candidate'))
    fig.update_xaxes(title='Objective f₁',range=[-.03,1.1],fixedrange=True)
    fig.update_yaxes(title='Objective f₂',range=[-.03,1.1],fixedrange=True)
    fig=chart(fig);fig.update_layout(showlegend=False)
    detail=f'ω = ({w[0]:.2f}, {w[1]:.2f}) · {len(candidates)} / 501 eligible reference points'
    if winner is not None: detail+=f' · selected ({x[winner]:.3f}, {y[winner]:.3f})'
    return fig,detail


WEIGHTS=np.column_stack((np.linspace(.1,.9,9),np.linspace(.9,.1,9)))
# Constructed surrogate-output example, independent of the trained ZDT2 model.
OFFSPRING=np.array([[.15+.09*i+.025*j,1.08-.085*i+.02*(2-j)] for i in range(9) for j in range(3)])


def neighbor_view(direction,k,stage):
    direction=int(direction);k=int(k)
    w=WEIGHTS[direction]
    distances=np.arccos(np.clip(WEIGHTS@w/(np.linalg.norm(WEIGHTS,axis=1)*np.linalg.norm(w)),-1,1))
    nearby=np.argsort(distances,kind='stable')[:k]
    ids=np.array([i*3+j for i in nearby for j in range(3)])
    angles=np.arccos(np.clip(OFFSPRING[ids]@w/(np.linalg.norm(OFFSPRING[ids],axis=1)*np.linalg.norm(w)),-1,1))
    survivors=ids[angles<=np.deg2rad(20)]
    winner=int(survivors[np.argmin(OFFSPRING[survivors]@w)]) if len(survivors) else None
    fig=go.Figure(go.Scatter(x=OFFSPRING[:,0],y=OFFSPRING[:,1],mode='markers',marker=dict(size=6,color='#dce1e8'),name='All proposals'))
    eligible=ids if stage=='pool' else survivors
    fig.add_trace(go.Scatter(x=OFFSPRING[eligible,0],y=OFFSPRING[eligible,1],mode='markers',marker=dict(size=10,color=BLUE),customdata=eligible,
        hovertemplate='Constructed proposal %{customdata}<br>(%{x:.3f}, %{y:.3f})<extra></extra>',name='Eligible proposals'))
    if stage=='select' and winner is not None:
        fig.add_trace(go.Scatter(x=[OFFSPRING[winner,0]],y=[OFFSPRING[winner,1]],mode='markers',marker=dict(symbol='star',size=17,color=PURPLE),name='Selected'))
    fig.add_trace(go.Scatter(x=[0,w[0]*1.5],y=[0,w[1]*1.5],mode='lines',line=dict(color=PURPLE,dash='dot'),showlegend=False,hoverinfo='skip'))
    fig.update_xaxes(title='Predicted objective 1',range=[0,1.25],fixedrange=True)
    fig.update_yaxes(title='Predicted objective 2',range=[0,1.25],fixedrange=True)
    fig=chart(fig);fig.update_layout(showlegend=False)
    summary=f'Direction {direction+1} · neighbors {", ".join(str(n+1) for n in nearby)} · pool {len(ids)}'
    if stage!='pool': summary+=f' → {len(survivors)} within cone'
    if stage=='select': summary+=f' → proposal {winner}' if winner is not None else ' · no survivor in this constructed example'
    return fig,summary


def rank_view(percentile,baseline):
    table_id='S4.T1' if str(percentile)=='100' else 'A1.T14'
    groups=TABLES[table_id]['columns'][1:]
    fig=go.Figure()
    for name,color in [('ParetoFlow',PURPLE),(baseline,BLUE)]:
        values=[cell(table_id,name,g)[0] for g in groups]
        labels=[cell(table_id,name,g)[2] for g in groups]
        fig.add_trace(go.Scatter(x=values,y=groups,mode='markers',name=name,marker=dict(size=11,color=color),customdata=labels,
            hovertemplate='%{y}<br>Reported rank %{customdata}<extra>%{fullData.name}</extra>'))
    fig.update_xaxes(title='Average rank ↓',range=[0,23],dtick=5)
    fig.update_yaxes(autorange='reversed')
    fig=chart(fig);fig.update_layout(margin=dict(l=85,r=20,t=32,b=45))
    pf=cell(table_id,'ParetoFlow','All Tasks')[2];other=cell(table_id,baseline,'All Tasks')[2]
    return fig,f'All tasks: ParetoFlow {pf}; {baseline} {other}. Hover for reported spread.',source_note(f'{table_id} · {percentile}th percentile · rank spread is not a confidence interval.',table_id)


def benchmark_view(task,percentile,baseline):
    tid=TASKS[task][str(percentile)]
    methods=['ParetoFlow',baseline]+([] if baseline=='D-Best' else ['D-Best'])
    fig=comparisons(tid,task,methods)
    a,b=task_cell(task,percentile,'ParetoFlow'),task_cell(task,percentile,baseline)
    if a[0] is None or b[0] is None:
        detail='N/A is not a zero: one requested result is not reported.'
    else:
        detail=f'{task} · ParetoFlow {a[2]} · {baseline} {b[2]} · difference {a[0]-b[0]:+.2f}'
    return fig,detail,source_note(f'{tid} · {percentile}th percentile · reported mean ± standard deviation; no local rerun.',tid)


def ablation_view(task,table_id):
    table=TABLES[table_id]
    if task not in table['columns']: task=table['columns'][1]
    fig=comparisons(table_id,task,[r[0] for r in table['rows']])
    return fig,f'{task} · {table["caption"]}',source_note(f'{table_id} · published mean ± standard deviation. Changes are not additive component contributions.',table_id)


def cost_view(scope):
    tid='A1.T5' if scope=='representative' else 'A1.T7'
    table=TABLES[tid];tasks=table['columns'][1:]
    rownames=[r[0] for r in table['rows'] if 'training (min)' in r[0].lower() or 'sampling (min)' in r[0].lower()]
    fig=go.Figure()
    for name,color in zip(rownames,[GRAY,BLUE,PURPLE]):
        fig.add_trace(go.Bar(x=tasks,y=[cell(tid,name,t)[0] for t in tasks],name=name.replace(' (min)',''),marker_color=color))
    fig.update_yaxes(title='Time (minutes)',rangemode='tozero')
    fig=chart(fig);fig.update_layout(barmode='stack',margin=dict(l=50,r=10,t=45,b=60),legend=dict(y=1.22,font=dict(size=10)))
    return fig,'Reported hardware: Intel i9-12900K + NVIDIA RTX 3090. These are the paper’s timings.',source_note(f'{tid} · training and sampling shown separately; not measured on this computer.',tid)


def make_paper_panels(server):
    apps={}
    for name in ['method','guidance','neighbors','ranks','benchmarks','paper-ablation','cost','tables']:
        apps[name]=Dash('paper_'+name.replace('-','_'),server=server,url_base_pathname=f'/{name}/',assets_folder='assets',title='ParetoFlow · '+name)
        server.add_url_rule('/'+name,endpoint='paper_redirect_'+name,view_func=lambda name=name:redirect('/'+name+'/'))
    method=apps['method']
    method.layout=html.Div([head('One pass through ParetoFlow','METHOD WALKTHROUGH','S3'),
        dcc.RadioItems(id='method-step',options=[{'label':str(i+1),'value':i} for i in range(7)],value=0,inline=True,className='method-steps'),
        dcc.Graph(id='method-plot',config=CONFIG,style={'height':'170px'}),html.Div(id='method-detail',className='method-detail'),
        foot('Select a stage to connect the algorithm’s operations. This is an explanatory diagram, not a recorded trajectory.')],className='paper-panel')
    method.callback(Output('method-plot','figure'),Output('method-detail','children'),Input('method-step','value'))(method_view)
    guidance=apps['guidance']
    guidance.layout=html.Div([head('Why a weighted sum needs local filtering','GEOMETRIC ILLUSTRATION','S3.SS1'),
        html.Div([dropdown('front-shape',[('nonconvex','Non-convex · ZDT2 front'),('convex','Convex · ZDT1 front')],'nonconvex'),
            dcc.Checklist(id='cone',options=[{'label':'Local cone','value':'on'}],value=['on'])],className='paper-controls'),
        html.Div([html.Span('Weight ω₁'),dcc.Slider(id='weight',min=.1,max=.9,step=.05,value=.5,marks={.1:'0.1',.5:'0.5',.9:'0.9'})],className='paper-slider'),
        graph('guidance-plot'),html.Div(id='guidance-detail',className='mini-readout'),
        foot('Analytic front, 501 reference points, fixed 8° half-cone for illustration. The real algorithm uses predicted objectives and a direction-dependent cone.')],className='paper-panel')
    guidance.callback(Output('guidance-plot','figure'),Output('guidance-detail','children'),Input('front-shape','value'),Input('weight','value'),Input('cone','value'))(guidance_view)
    neighbor=apps['neighbors']
    neighbor.layout=html.Div([head('Borrow proposals from nearby directions','CONSTRUCTED EXAMPLE','S3.SS2'),
        html.Div([dropdown('neighbor-direction',[(i,f'Direction {i+1}') for i in range(9)],4),dropdown('neighbor-k',[(1,'K = 1'),(3,'K = 3'),(5,'K = 5')],3),
            dropdown('neighbor-stage',[('pool','1 · Pool'),('filter','2 · Filter'),('select','3 · Select')],'pool')],className='paper-controls'),
        graph('neighbor-plot'),html.Div(id='neighbor-detail',className='mini-readout'),
        foot('Nine constructed directions, three proposals each, fixed 20° half-cone. Colors reveal pooling and selection; these points are not experimental samples.')],className='paper-panel')
    neighbor.callback(Output('neighbor-plot','figure'),Output('neighbor-detail','children'),Input('neighbor-direction','value'),Input('neighbor-k','value'),Input('neighbor-stage','value'))(neighbor_view)
    rank=apps['ranks']
    choices=[(m,m) for m in METHODS if m!='ParetoFlow']
    rank.layout=html.Div([head('Compare average rank across task families','PAPER RESULTS','S4.T1'),
        html.Div([dropdown('rank-percentile',[('100','100th percentile'),('50','50th percentile')],'100'),dropdown('rank-baseline',choices,'MM')],className='paper-controls'),
        graph('rank-plot'),html.Div(id='rank-detail',className='mini-readout'),html.Div(id='rank-source',className='paper-foot')],className='paper-panel')
    rank.callback(Output('rank-plot','figure'),Output('rank-detail','children'),Output('rank-source','children'),Input('rank-percentile','value'),Input('rank-baseline','value'))(rank_view)
    bench=apps['benchmarks']
    bench.layout=html.Div([head('Check the result on a particular task','PAPER RESULTS · 52 TASKS','A1.SS6'),
        html.Div([dropdown('bench-task',[(t,TASKS[t]['family']+' · '+t) for t in TASKS],'ZDT2'),dropdown('bench-percentile',[('100','100th percentile'),('50','50th percentile')],'100'),dropdown('bench-baseline',choices,'MM')],className='paper-controls'),
        graph('bench-plot'),html.Div(id='bench-detail',className='mini-readout'),html.Div(id='bench-source',className='paper-foot')],className='paper-panel')
    bench.callback(Output('bench-plot','figure'),Output('bench-detail','children'),Output('bench-source','children'),Input('bench-task','value'),Input('bench-percentile','value'),Input('bench-baseline','value'))(benchmark_view)
    ablation=apps['paper-ablation']
    ablation.layout=html.Div([head('Which changes weaken the reported result?','PAPER ABLATIONS','S4.T2'),
        html.Div([dropdown('paper-abl-table',[('S4.T2','Main components · Table 2'),('A1.T3','Other EAs · Table 3'),('A1.T4','Predictor choice · Table 4'),('A1.T21','Flow vs diffusion · Table 21'),('A1.T22','Weight generation · Table 22'),('A1.T23','Remove EA · Table 23')],'S4.T2'),dropdown('paper-abl-task',[(t,t) for t in TABLES['S4.T2']['columns'][1:]],'ZDT2')],className='paper-controls'),
        graph('paper-abl-plot'),html.Div(id='paper-abl-detail',className='mini-readout'),html.Div(id='paper-abl-source',className='paper-foot')],className='paper-panel')
    @ablation.callback(Output('paper-abl-task','options'),Output('paper-abl-task','value'),Input('paper-abl-table','value'))
    def choose_ablation_table(table_id):
        tasks=TABLES[table_id]['columns'][1:]
        return [{'label':t,'value':t} for t in tasks],tasks[0]
    ablation.callback(Output('paper-abl-plot','figure'),Output('paper-abl-detail','children'),Output('paper-abl-source','children'),Input('paper-abl-task','value'),Input('paper-abl-table','value'))(ablation_view)
    cost=apps['cost']
    cost.layout=html.Div([head('Separate training cost from sampling cost','PAPER TIMINGS','A1.T5'),
        html.Div(dropdown('cost-scope',[('representative','Representative tasks · Table 5'),('scaling','NAS and control · Table 7')],'representative'),className='paper-controls'),
        graph('cost-plot'),html.Div(id='cost-detail',className='mini-readout'),html.Div(id='cost-source',className='paper-foot')],className='paper-panel')
    cost.callback(Output('cost-plot','figure'),Output('cost-detail','children'),Output('cost-source','children'),Input('cost-scope','value'))(cost_view)
    tables=apps['tables']
    tables.layout=html.Div([head('All 23 source tables','PAPER DATA LIBRARY','S4.T1'),dcc.Location(id='table-location'),
        html.Div(dropdown('table-choice',[(t['id'],t['caption']) for t in PAPER['tables']],'S4.T1'),className='paper-controls'),
        html.Div(id='table-caption',className='mini-readout'),dash_table.DataTable(id='source-table',page_size=22,filter_action='native',sort_action='custom',sort_by=[],
            style_table={'overflowX':'auto'},style_cell={'fontFamily':'Arial','fontSize':13,'padding':'8px','textAlign':'left','minWidth':'95px'},style_header={'fontWeight':'bold','backgroundColor':'#f0edf7'}),
        html.Div([html.A('Download this table (CSV)',id='table-download'),html.A('Download all tables (JSON)',href='/paper-data')],className='paper-links'),
        foot('Source: Yuan, Chen, Pal & Liu (2025), arXiv v2, CC BY 4.0. Cells preserve reported text; numeric columns sort by the reported mean. N/A remains unavailable and sorts last.')],className='paper-panel paper-library')
    @tables.callback(Output('table-choice','value'),Input('table-location','search'))
    def table_from_url(search):
        key=parse_qs((search or '').lstrip('?')).get('table',['S4.T1'])[0]
        return key if key in TABLES else 'S4.T1'
    @tables.callback(Output('source-table','columns'),Output('source-table','data'),Output('table-caption','children'),Output('table-download','href'),Input('table-choice','value'),Input('source-table','sort_by'))
    def show_table(key,sort_by):
        table=TABLES[key]
        return [{'name':c,'id':str(i)} for i,c in enumerate(table['columns'])],[{str(i):v for i,v in enumerate(r)} for r in sorted_source_rows(key,sort_by)],source_note(table['caption'],key),f'/paper-table/{key}.csv'
    @server.get('/paper-data')
    def paper_data(): return jsonify(PAPER)
    @server.get('/paper-table/<key>.csv')
    def paper_csv(key):
        if key not in TABLES: return 'Table not found',404
        out=io.StringIO();writer=csv.writer(out);writer.writerow(TABLES[key]['columns']);writer.writerows(TABLES[key]['rows'])
        return Response('\ufeff'+out.getvalue(),mimetype='text/csv',headers={'Content-Disposition':f'attachment; filename="paretoflow-{key}.csv"'})
    return apps
