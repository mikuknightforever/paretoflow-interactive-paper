"""Interactive constructed geometry; no paper-table values or model outputs."""
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html, no_update
from flask import redirect


INK = '#142b42'
TEAL = '#078783'
AMBER = '#d18b27'
VIOLET = '#7861ae'
MUTED = '#617486'
PALE = '#dce6ed'
CONFIG = {'displayModeBar': False, 'responsive': True}
GUIDANCE_PROVENANCE = (
    'Constructed geometry: 501 points on analytic ZDT1 / ZDT2 reference fronts. '
    'The adjustable cone illustrates selection; it is not a reconstruction of Figure 2 '
    'or a recorded ParetoFlow run. The sampler uses predicted, standardized scores '
    'and a direction-dependent cone.'
)
NEIGHBOR_PROVENANCE = (
    'Constructed geometry: nine fixed directions and three fixed proposal points per direction. '
    'These 27 coordinates are teaching examples, not recorded offspring or benchmark results. '
    'The cone has a fixed 20° half-angle; no survivor is invented when it is empty.'
)
WEIGHTS = np.column_stack((np.linspace(.1, .9, 9), np.linspace(.9, .1, 9)))
OFFSPRING = np.array([[.15 + .09*i + .025*j, 1.08 - .085*i + .02*(2-j)]
                      for i in range(9) for j in range(3)])


def guidance_geometry(shape='nonconvex', weight=.5, half_angle=8):
    """Compare the same weighted minimization with and without the angular filter."""
    if shape not in ('convex', 'nonconvex'):
        raise ValueError('Unknown analytic front')
    weight, half_angle = float(weight), float(half_angle)
    if not np.isfinite(weight) or not .1 <= weight <= .9:
        raise ValueError('Weight must be between 0.1 and 0.9')
    if not np.isfinite(half_angle) or not 2 <= half_angle <= 30:
        raise ValueError('Half-angle must be between 2 and 30 degrees')
    x = np.linspace(0, 1, 501)
    points = np.column_stack((x, 1-np.sqrt(x) if shape == 'convex' else 1-x*x))
    weights = np.array([weight, 1-weight])
    scores = points @ weights
    cosine = points @ weights / (np.linalg.norm(points, axis=1)*np.linalg.norm(weights))
    angles = np.degrees(np.arccos(np.clip(cosine, -1, 1)))
    admitted = np.flatnonzero(angles <= half_angle)
    before = int(np.argmin(scores))
    after = int(admitted[np.argmin(scores[admitted])]) if len(admitted) else None
    return dict(points=points, weights=weights, scores=scores, angles=angles,
                admitted=admitted, before=before, after=after, half_angle=half_angle,
                before_ties=int(np.isclose(scores, scores[before], atol=1e-12, rtol=0).sum()))


def neighbor_geometry(direction=4, k=3):
    """Pool fixed offspring from the K closest directions, then filter and score."""
    direction, k = int(direction), int(k)
    if not 0 <= direction < 9 or k not in (1, 3, 5):
        raise ValueError('Choose direction 1–9 and K = 1, 3 or 5')
    weight = WEIGHTS[direction]
    cosine = WEIGHTS @ weight / (np.linalg.norm(WEIGHTS, axis=1)*np.linalg.norm(weight))
    distances = np.arccos(np.clip(cosine, -1, 1))
    neighbors = np.argsort(distances, kind='stable')[:k]
    pool = np.array([i*3+j for i in neighbors for j in range(3)], dtype=int)
    points = OFFSPRING[pool]
    angles = np.degrees(np.arccos(np.clip(
        points @ weight / (np.linalg.norm(points, axis=1)*np.linalg.norm(weight)), -1, 1)))
    admitted = pool[angles <= 20]
    scores = OFFSPRING @ weight
    winner = int(admitted[np.argmin(scores[admitted])]) if len(admitted) else None
    return dict(direction=direction, k=k, weight=weight, neighbors=neighbors,
                pool=pool, angles=angles, admitted=admitted, scores=scores, winner=winner)


def _figure(height=300, x_title='Objective f₁ ↓', y_title='Objective f₂ ↓'):
    fig = go.Figure()
    fig.update_layout(template='plotly_white', height=height,
                      paper_bgcolor='white', plot_bgcolor='white',
                      margin=dict(l=44, r=16, t=16, b=42),
                      font=dict(family='Arial, sans-serif', size=11, color=INK),
                      showlegend=False, dragmode=False, hovermode='closest')
    fig.update_xaxes(title=x_title, range=[-.035, 1.15], fixedrange=True,
                     gridcolor='#edf2f5', zeroline=False, constrain='domain')
    fig.update_yaxes(title=y_title, range=[-.035, 1.17], fixedrange=True,
                     gridcolor='#edf2f5', zeroline=False, scaleanchor='x',
                     scaleratio=1, constrain='domain')
    return fig


def _cone(fig, weight, half_angle):
    theta = np.arctan2(weight[1], weight[0])
    ends = np.clip([theta-np.deg2rad(half_angle), theta+np.deg2rad(half_angle)], 0, np.pi/2)
    fig.add_trace(go.Scatter(x=[0, 1.7*np.cos(ends[0]), 1.7*np.cos(ends[1]), 0],
                             y=[0, 1.7*np.sin(ends[0]), 1.7*np.sin(ends[1]), 0],
                             fill='toself', fillcolor='rgba(7,135,131,.085)',
                             line=dict(width=0), hoverinfo='skip', name='Illustrative cone'))


def _weight_ray(fig, weight):
    unit = weight/np.linalg.norm(weight)
    fig.add_trace(go.Scatter(x=[0, unit[0]*1.5], y=[0, unit[1]*1.5], mode='lines',
                             line=dict(color=VIOLET, width=1.5, dash='dot'),
                             hoverinfo='skip', name='Weight direction'))


def guidance_figure(data, filtered):
    points, weight = data['points'], data['weights']
    fig = _figure()
    if filtered:
        _cone(fig, weight, data['half_angle'])
    fig.add_trace(go.Scatter(x=points[:, 0], y=points[:, 1], mode='lines',
                             line=dict(color=PALE if filtered else TEAL, width=3),
                             name='Analytic reference front',
                             hovertemplate='f₁ %{x:.3f}<br>f₂ %{y:.3f}<extra>Reference point</extra>'))
    if filtered:
        ids = data['admitted']
        fig.add_trace(go.Scatter(x=points[ids, 0], y=points[ids, 1], mode='lines+markers',
                                 marker=dict(size=3, color=TEAL), line=dict(color=TEAL, width=5),
                                 name='Eligible reference points',
                                 hovertemplate='f₁ %{x:.3f}<br>f₂ %{y:.3f}<extra>Inside cone</extra>'))
        before = points[data['before']]
        fig.add_trace(go.Scatter(x=[before[0]], y=[before[1]], mode='markers',
                                 marker=dict(size=13, color=MUTED, symbol='circle-open', line=dict(width=2)),
                                 name='Unfiltered choice', hovertemplate='Choice before filtering<extra></extra>'))
    _weight_ray(fig, weight)
    winner = data['after'] if filtered else data['before']
    if winner is not None:
        point, score = points[winner], data['scores'][winner]
        x = np.linspace(0, 1.1, 200)
        y = (score-weight[0]*x)/weight[1]
        visible = (y >= 0) & (y <= 1.12)
        fig.add_trace(go.Scatter(x=x[visible], y=y[visible], mode='lines',
                                 line=dict(color=AMBER, dash='dash', width=1), hoverinfo='skip',
                                 name='Equal weighted loss'))
        fig.add_trace(go.Scatter(x=[point[0]], y=[point[1]], mode='markers',
                                 marker=dict(size=17, symbol='star', color=AMBER,
                                             line=dict(color='white', width=1)),
                                 name='Selected candidate',
                                 hovertemplate=f'Chosen point<br>f₁ %{{x:.3f}} · f₂ %{{y:.3f}}<br>Weighted loss {score:.4f}<extra></extra>'))
    return fig


def direction_figure(data):
    fig = _figure(185, 'ω₁ / ‖ω‖', 'ω₂ / ‖ω‖')
    fig.update_layout(margin=dict(l=36, r=16, t=6, b=34), clickmode='event')
    fig.update_xaxes(range=[-.035, 1.12], dtick=.5)
    fig.update_yaxes(range=[-.035, 1.12], dtick=.5, scaleanchor='x', scaleratio=1)
    units = WEIGHTS/np.linalg.norm(WEIGHTS, axis=1)[:, None]
    for i, point in enumerate(units):
        color = INK if i == data['direction'] else TEAL if i in data['neighbors'] else PALE
        fig.add_trace(go.Scatter(x=[0, point[0]], y=[0, point[1]], mode='lines',
                                 line=dict(color=color, width=2 if i in data['neighbors'] else 1),
                                 hoverinfo='skip'))
    colors = [INK if i == data['direction'] else TEAL if i in data['neighbors'] else PALE for i in range(9)]
    fig.add_trace(go.Scatter(x=units[:, 0], y=units[:, 1], mode='markers+text',
                             text=[str(i+1) for i in range(9)], textposition='middle center',
                             textfont=dict(color='white', size=10), customdata=list(range(9)),
                             marker=dict(size=[22 if i == data['direction'] else 18 for i in range(9)],
                                         color=colors, line=dict(color='white', width=1)),
                             hovertemplate='Direction %{text}<br>Click to receive its neighbors<extra></extra>'))
    return fig


def neighbor_figures(data, stage='pool'):
    if stage not in ('pool', 'filter', 'select'):
        raise ValueError('Unknown neighboring stage')
    pool, admitted, winner = data['pool'], data['admitted'], data['winner']
    filtered = stage != 'pool'
    fig = _figure(265, 'Constructed objective 1 ↓', 'Constructed objective 2 ↓')
    if filtered:
        _cone(fig, data['weight'], 20)
    fig.add_trace(go.Scatter(x=OFFSPRING[:, 0], y=OFFSPRING[:, 1], mode='markers',
                             marker=dict(size=6, color=PALE), name='All 27 proposals',
                             hoverinfo='skip'))
    _weight_ray(fig, data['weight'])
    if filtered:
        excluded = np.setdiff1d(pool, admitted)
        fig.add_trace(go.Scatter(x=OFFSPRING[excluded, 0], y=OFFSPRING[excluded, 1], mode='markers',
                                 marker=dict(size=9, color=MUTED, symbol='x'), customdata=excluded,
                                 name='Excluded proposals', hovertemplate='P%{customdata}: outside cone<extra></extra>'))
    visible = admitted if filtered else pool
    fig.add_trace(go.Scatter(x=OFFSPRING[visible, 0], y=OFFSPRING[visible, 1], mode='markers',
                             marker=dict(size=11, color=TEAL, line=dict(color='white', width=1)),
                             customdata=[[int(i), int(i//3)+1, float(data['scores'][i])] for i in visible],
                             name='Pooled candidates' if not filtered else 'Admitted candidates',
                             hovertemplate='P%{customdata[0]} · direction %{customdata[1]}<br>Weighted loss %{customdata[2]:.4f}<extra></extra>'))
    if stage == 'select' and winner is not None:
        fig.add_trace(go.Scatter(x=[OFFSPRING[winner, 0]], y=[OFFSPRING[winner, 1]], mode='markers+text',
                                 marker=dict(size=20, color=AMBER, symbol='star', line=dict(color='white', width=1)),
                                 text=[f'P{winner}'], textposition='top center', textfont=dict(size=10, color=AMBER),
                                 name='Selected candidate', hovertemplate=f'P{winner} wins among admitted proposals<extra></extra>'))
    ordered = pool[np.argsort(data['scores'][pool], kind='stable')]
    colors = [AMBER if stage == 'select' and i == winner else MUTED if filtered and i not in admitted else TEAL for i in ordered]
    ranking = go.Figure(go.Bar(x=data['scores'][ordered], y=[f'P{i} · D{i//3+1}' for i in ordered],
                               orientation='h', marker_color=colors,
                               customdata=['Outside cone' if filtered and i not in admitted else 'Eligible' if filtered else 'In pool' for i in ordered],
                               hovertemplate='%{y}<br>Weighted loss %{x:.4f}<br>%{customdata}<extra></extra>'))
    ranking.update_layout(template='plotly_white', height=265, margin=dict(l=70, r=18, t=12, b=42),
                          paper_bgcolor='white', plot_bgcolor='white', showlegend=False, dragmode=False,
                          font=dict(family='Arial, sans-serif', size=10, color=INK), bargap=.3)
    ranking.update_xaxes(title='Weighted loss ↓', rangemode='tozero', fixedrange=True, gridcolor='#edf2f5')
    ranking.update_yaxes(autorange='reversed', fixedrange=True)
    return fig, ranking


def _stat(value, label):
    return html.Div([html.Strong(value), html.Span(label)], className='atelier-stat')


def _graph(id, figure=None):
    height = int(figure.layout.height) if figure is not None and figure.layout.height else 300
    return dcc.Graph(id=id, figure=figure, config=CONFIG, responsive=True,
                     style={'height': f'{height}px'})


def _card(title, subtitle, children):
    return html.Section([html.Div([html.H3(title), html.Span(subtitle)], className='atelier-card-head'),
                         *children], className='atelier-card')


def _head(kicker, title, subtitle):
    return html.Div(html.Div([
        html.Div(kicker, className='atelier-eyebrow'), html.H2(title),
        html.P(subtitle, className='atelier-subtitle'),
    ]), className='atelier-head')


def _legend():
    return html.Div([html.Span([html.Span('● ', style={'color': TEAL}), 'Eligible']),
                     html.Span([html.Span('★ ', style={'color': AMBER}), 'Selected']),
                     html.Span([html.Span('○ ', style={'color': MUTED}), 'Before filtering']),
                     html.Span([html.Span('┄ ', style={'color': VIOLET}), 'Weight direction'])],
                    className='atelier-legend')


def _guidance_layout():
    data = guidance_geometry()
    return html.Div([
        _head('GEOMETRY LAB / LOCAL FILTERING', 'Same preference. A different eligible set.',
              'Move the weight or cone width. Both panels solve the same weighted minimization.'),
        html.Div([
            html.Div([html.Label('Reference front', htmlFor='ga-shape'),
                      dcc.RadioItems(id='ga-shape', options=[{'label': 'Non-convex · ZDT2', 'value': 'nonconvex'},
                                      {'label': 'Convex · ZDT1', 'value': 'convex'}],
                                     value='nonconvex', inline=True, className='atelier-segments')], className='atelier-field'),
            html.Div([html.Label('Weight ω₁', htmlFor='ga-weight'),
                      dcc.Slider(id='ga-weight', min=.1, max=.9, step=.05, value=.5,
                                 marks={.1: '.1', .5: '.5', .9: '.9'}, tooltip={'placement': 'bottom'})], className='atelier-field'),
            html.Div([html.Label('Cone half-angle', htmlFor='ga-angle'),
                      dcc.Slider(id='ga-angle', min=2, max=30, step=1, value=8,
                                 marks={2: '2°', 8: '8°', 20: '20°', 30: '30°'}, tooltip={'placement': 'bottom'})], className='atelier-field'),
        ], className='atelier-controls'),
        html.Div([
            _card('Before filtering', 'Every reference point can compete', [_graph('ga-before', guidance_figure(data, False))]),
            _card('After filtering', 'Only points inside the cone can compete', [_graph('ga-after', guidance_figure(data, True))]),
        ], className='atelier-grid'),
        _legend(),
        html.Div(id='ga-stats', className='atelier-stats', role='status', **{'aria-live': 'polite'}),
        html.Div(id='ga-insight', className='atelier-status'),
        html.P(GUIDANCE_PROVENANCE, className='atelier-note'),
    ], className='atelier atelier-panel')


def render_guidance(shape, weight, half_angle):
    data = guidance_geometry(shape, weight, half_angle)
    before, after = data['before'], data['after']
    point = lambda idx: 'None' if idx is None else f"({data['points'][idx, 0]:.3f}, {data['points'][idx, 1]:.3f})"
    stats = [_stat(f"({data['weights'][0]:.2f}, {data['weights'][1]:.2f})", 'Weight vector'),
             _stat(f"{len(data['admitted'])} / 501", 'Inside the cone'),
             _stat(point(before), 'Unfiltered choice'), _stat(point(after), 'Filtered choice')]
    if after is None:
        insight = 'This cone contains no sampled reference point. No filtered winner is shown.'
    elif before == after:
        insight = 'The unconstrained minimizer is already inside the cone. Filtering preserves this choice.'
    else:
        delta = data['scores'][after]-data['scores'][before]
        insight = (f"Filtering moves the choice into the requested region. Weighted loss increases by {delta:.4f}; "
                   'the benefit illustrated here is access to a different trade-off, not a smaller weighted loss.')
    if data['before_ties'] > 1:
        insight += f" The unfiltered problem has {data['before_ties']} tied sampled minimizers; the first is shown."
    return guidance_figure(data, False), guidance_figure(data, True), stats, insight


def _neighbor_layout():
    data = neighbor_geometry()
    objective, ranking = neighbor_figures(data)
    return html.Div([
        _head('GEOMETRY LAB / NEIGHBORING EVOLUTION', 'Let nearby directions share their proposals.',
              'Pick a receiving direction, widen its neighborhood, then filter and select.'),
        html.Div([
            html.Div([html.Label('Receiving direction', htmlFor='ng-direction'),
                      dcc.Dropdown(id='ng-direction', options=[{'label': f'Direction {i+1}', 'value': i} for i in range(9)],
                                   value=4, clearable=False)], className='atelier-field'),
            html.Div([html.Label('Neighborhood size · including itself'),
                      dcc.RadioItems(id='ng-k', options=[{'label': f'K = {k}', 'value': k} for k in (1, 3, 5)],
                                     value=3, inline=True, className='atelier-segments')], className='atelier-field'),
            html.Div([html.Label('Inspect a decision'),
                      dcc.RadioItems(id='ng-stage', options=[{'label': label, 'value': value} for label, value in
                                      [('1 · Pool', 'pool'), ('2 · Filter', 'filter'), ('3 · Select', 'select')]],
                                     value='pool', inline=True, className='atelier-segments')], className='atelier-field'),
        ], className='atelier-controls'),
        html.Div([
            _card('Choose a direction', 'Click a numbered point · teal marks its neighbors', [_graph('ng-directions', direction_figure(data))]),
            _card('Follow the candidate set', 'Three fixed proposals originate from every direction',
                  [html.Div(id='ng-stats', className='atelier-stats',
                            style={'gridTemplateColumns': 'repeat(3, minmax(0, 1fr))'}),
                   html.Div(id='ng-insight', className='atelier-status', role='status', **{'aria-live': 'polite'})]),
        ], className='atelier-grid'),
        html.Div([
            _card('Candidate space', 'Teal: eligible · ×: excluded · ★: selected', [_graph('ng-objective', objective)]),
            _card('Score ordering', 'Best weighted loss first; excluded candidates cannot win', [_graph('ng-ranking', ranking)]),
        ], className='atelier-grid', style={'marginTop': '12px'}),
        html.P(NEIGHBOR_PROVENANCE, className='atelier-note'),
    ], className='atelier atelier-panel')


def render_neighbors(direction, k, stage):
    data = neighbor_geometry(direction, k)
    objective, ranking = neighbor_figures(data, stage)
    filtered = stage != 'pool'
    stats = [_stat(str(len(data['pool'])), 'Pooled proposals'),
             _stat(str(len(data['admitted'])) if filtered else '—', 'Admitted by cone'),
             _stat(f"P{data['winner']}" if stage == 'select' and data['winner'] is not None else '—', 'Selected proposal')]
    neighbors = ', '.join(str(i+1) for i in data['neighbors'])
    if stage == 'pool':
        insight = f"Direction {int(direction)+1} receives {int(k)} × 3 proposals from directions {neighbors}. The bars order the full pool before filtering."
    elif not len(data['admitted']):
        insight = 'No pooled proposal is inside this 20° cone. This constructed example has no survivor and no selected point.'
    elif stage == 'filter':
        insight = f"The 20° cone admits {len(data['admitted'])} of {len(data['pool'])} pooled proposals. Gray bars remain visible to show what was excluded."
    else:
        winner = data['winner']
        source = 'its own direction' if winner//3 == int(direction) else f'neighbor direction {winner//3+1}'
        insight = f"P{winner} wins among admitted proposals, with loss {data['scores'][winner]:.4f}. It comes from {source}."
    return direction_figure(data), objective, ranking, stats, insight


def create_geometry_panels(server):
    """Mount the two geometry panels. The caller must not mount the old routes."""
    apps = {}
    for name in ('guidance', 'neighbors'):
        apps[name] = Dash('geometry_'+name, server=server, url_base_pathname=f'/{name}/',
                          assets_folder=str(Path(__file__).resolve().parent/'assets'),
                          title='ParetoFlow · '+name.title())
        server.add_url_rule('/'+name, endpoint='geometry_redirect_'+name,
                            view_func=lambda name=name: redirect('/'+name+'/'))
    guidance = apps['guidance']
    guidance.layout = _guidance_layout()
    guidance.callback(Output('ga-before', 'figure'), Output('ga-after', 'figure'),
                      Output('ga-stats', 'children'), Output('ga-insight', 'children'),
                      Input('ga-shape', 'value'), Input('ga-weight', 'value'), Input('ga-angle', 'value'))(render_guidance)
    neighbor = apps['neighbors']
    neighbor.layout = _neighbor_layout()
    @neighbor.callback(Output('ng-direction', 'value'), Input('ng-directions', 'clickData'), prevent_initial_call=True)
    def choose_direction(click):
        if click and click.get('points'):
            value = click['points'][0].get('customdata')
            if isinstance(value, (int, float)) and value == int(value) and 0 <= value < 9:
                return int(value)
        return no_update
    neighbor.callback(Output('ng-directions', 'figure'), Output('ng-objective', 'figure'),
                      Output('ng-ranking', 'figure'), Output('ng-stats', 'children'),
                      Output('ng-insight', 'children'), Input('ng-direction', 'value'),
                      Input('ng-k', 'value'), Input('ng-stage', 'value'))(render_neighbors)
    return apps
