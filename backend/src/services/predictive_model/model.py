
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
import polars as pl
from typing import Tuple
class Model:
    def __init__(self, player_stats_df: pl.DataFrame, team_stats_df: pl.DataFrame, team_matchups_df: pl.DataFrame, model = None):
        self.player_stats_df = player_stats_df
        self.team_stats_df = team_stats_df
        self.team_matchups_df = team_matchups_df
        self.model = model

    def run(self):
        merged_teams_player_stats_df, team_matchups_df = self._prepare_data()
        classification_report = self._train_model(team_matchups_df)
        return classification_report
    
    def _prepare_data(self) -> Tuple[pl.DataFrame, pl.DataFrame]:
        merged_teams_player_stats_df = self.team_stats_df.join(self.player_stats_df, on=["team_id", "season_id"], how="inner")
        team_matchups_df = self.team_matchups_df.with_columns([pl.when(pl.col("team_win_loss") == "W").then(1).otherwise(0).alias("team_win")])
        team_matchups_df = team_matchups_df.with_columns([
            pl.when(pl.col("team_win") == 1).then(0).otherwise(1).alias("win"),
            pl.when(pl.col("team_win") == 0).then(0).otherwise(1).alias("loss")
        ])

        return merged_teams_player_stats_df, team_matchups_df
        
    def _train_model(self, df: pl.DataFrame):
        X = df.select(['team_id',
                        'team_field_goal_percentage', 
                        'opponent_field_goal_percentage', 
        ])
        y = df.select("team_win")

        X_np = X.to_numpy()
        y_np = y.to_numpy().ravel()

        X_train, X_test, y_train, y_test = train_test_split(X_np, y_np, test_size=0.2, random_state=42)

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        print("Accuracy:", accuracy_score(y_test, y_pred))
        print(classification_report(y_test, y_pred))

        return classification_report(y_test, y_pred)
