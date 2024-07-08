from collections import defaultdict

import pandas as pd
import plotly.graph_objects as go


class StatisticsService:
    @staticmethod
    def get_new_users_chart(users, period :str):
        data = StatisticsService.count_users(users)

        df = pd.DataFrame(data.items(), columns=['date', 'new_users'])
        df['date'] = pd.to_datetime(df['date'])

        if period == "week":
            period = "неделю"
        else:
            period = "месяц"

        fig = go.Figure(data=[go.Scatter(
            x=df['date'],
            y=df['new_users'],
            mode='lines+markers',
            name='Новые пользователи'
        )])

        fig.update_layout(
            title=f"Новые пользователи за {period}",
            xaxis_title="Дата",
            yaxis_title="Количество новых пользователей",
            showlegend=True
        )

        return fig.to_json()


    @staticmethod
    def count_users(users):
        registration_counts = defaultdict(int)
        for user in users:
            registration_counts[
                user.registration_date.date()] += 1
        return dict(registration_counts)
