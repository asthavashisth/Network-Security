import yaml
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logger
import os
import sys
import numpy as np
import dill
import pickle
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import f1_score
import warnings


def read_yaml_file(file_path: str) -> dict:
    try:
        with open(file_path, 'rb') as file:
            content = yaml.safe_load(file)
            return content 
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e

def write_yaml_file(file_path: str, content:object,replace:bool=False) -> None:
    try:
        if replace:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as file:
            yaml.dump(content, file)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def save_numpy_array(file_path:str,array:np.array):
    try:
        dir_path=os.path.dirname(file_path)
        os.makedirs(dir_path,exist_ok=True)
        with open(file_path , "wb") as file_obj:
            np.save(file_obj,array)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def save_object(file_path:str,obj:object)->None:
    try:
        logger.info("Entered save object method")
        dir_path=os.path.dirname(file_path)
        os.makedirs(dir_path,exist_ok=True)
        with open(file_path , "wb") as file_obj:
            pickle.dump(obj,file_obj)
        logger.info("Exited save object method")
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def load_object(file_path:str)->object:
    try:
        if not os.path.exists(file_path):
            raise Exception("The file not exists")
        with open(file_path , "rb") as file_obj:
            print(file_obj)
            return pickle.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def load_numpy_array(file_path:str)->np.array:
    try:
        with open(file_path , "rb") as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e





warnings.filterwarnings("ignore")

from sklearn.model_selection import GridSearchCV
from sklearn.metrics import f1_score

def evaluate_models(x_train, y_train, x_test, y_test, models: dict, param: dict):
    try:
        report = {}
        best_score = -1
        best_model = None
        best_model_name = None

        for model_name, model in models.items():
            print(f"\n🔍 Tuning hyperparameters for: {model_name}")
            if model_name not in param:
                print(f"⚠️ Skipping {model_name} as it has no parameters to tune.")
                continue

            grid = GridSearchCV(
                estimator=model,
                param_grid=param[model_name],
                scoring="f1_weighted",
                cv=3,
                verbose=1,
                n_jobs=-1,
                error_score='raise'
            )

            grid.fit(x_train, y_train)
            best_estimator = grid.best_estimator_

            y_test_pred = best_estimator.predict(x_test)
            f1 = f1_score(y_test, y_test_pred, average="weighted")

            print(f"✅ {model_name} | Best F1 Score: {f1:.4f}")
            report[model_name] = f1

            if f1 > best_score:
                best_score = f1
                best_model = best_estimator
                best_model_name = model_name

        return report, best_model_name, best_model

    except Exception as e:
        raise NetworkSecurityException(e, sys)
