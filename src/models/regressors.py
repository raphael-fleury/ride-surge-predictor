from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from config.model_params import RF_PARAMS, XGB_PARAMS, LGBM_PARAMS

def get_models():
    """Returns a dictionary of un-fitted scikit-learn compatible models."""
    return {
        "Regressão Linear (Baseline)": LinearRegression(),
        "Random Forest": RandomForestRegressor(**RF_PARAMS),
        "XGBoost": XGBRegressor(**XGB_PARAMS),
        "LightGBM": LGBMRegressor(**LGBM_PARAMS)
    }