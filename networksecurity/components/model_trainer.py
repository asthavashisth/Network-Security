import os
import sys
import warnings
warnings.filterwarnings("ignore")

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logger

from networksecurity.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact
from networksecurity.entity.config_entity import ModelTrainerConfig

from networksecurity.utils.main_utils.utils import save_object,load_numpy_array,load_object,evaluate_models
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score
from networksecurity.utils.ml_utils.model.estimator import NetworkModel

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)
import mlflow

import dagshub
dagshub.init(repo_owner='astha.vashisth136', repo_name='Network-Security', mlflow=True)

class ModelTrainer:
    def __init__(self,model_trainer_config:ModelTrainerConfig,data_transformation_artifact:DataTransformationArtifact):
        try:
            self.model_trainer_config=model_trainer_config
            self.data_transformation_artifact=data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def track_mlflow(self,best_model,classificationmetric):
        with mlflow.start_run():
            f1_score=classificationmetric.f1_score
            precision_score=classificationmetric.precision_score
            recall_score=classificationmetric.recall_score
            
            mlflow.log_metric("f1_score", f1_score)
            mlflow.log_metric("precision_score", precision_score)
            mlflow.log_metric("recall_score", recall_score)
            # mlflow.sklearn.log_model(best_model,"model")
        
    def train_model(self,x_train,y_train,x_test,y_test):
         models={
             "Random Forest":RandomForestClassifier(verbose=1),
             "Decision Tree":DecisionTreeClassifier(),
             "Gradient Boosting":GradientBoostingClassifier(verbose=1),
             "Logistic Regression":LogisticRegression(verbose=1),
             "AdaBoost":AdaBoostClassifier(),
         }
         params = {
            "Decision Tree": {
            "criterion": ['gini', 'entropy'],
            "splitter": ['best'],
            "max_features": ['sqrt']
        },

         "Random Forest": {
            "criterion": ['gini'],
            "max_features": ['sqrt'],
            "n_estimators": [50, 100]
        },

        "Gradient Boosting": {
            "loss": ['log_loss'],
            "learning_rate": [0.1],
            "subsample": [0.8],
            "criterion": ['friedman_mse'],
            "max_features": ['sqrt'],
            "n_estimators": [50, 100]
        },

        "Logistic Regression": {
            "C": [1.0],  
            "solver": ['lbfgs']
        },

        "AdaBoost": {
            "learning_rate": [0.1],
            "n_estimators": [50, 100]
        }
    }

         
         if len(set(y_train)) < 2:
            raise ValueError("Training data has only one class. Cannot train a classification model.")

         model_report, best_model_name, best_model = evaluate_models(
            x_train=x_train,
            y_train=y_train,
            x_test=x_test,
            y_test=y_test,
            models=models,
            param=params
          )



         y_train_pred=best_model.predict(x_train)

         classification_train_metric=get_classification_score(y_true=y_train,y_pred=y_train_pred)

         self.track_mlflow(best_model,classification_train_metric)


         y_test_pred=best_model.predict(x_test)
         classification_test_metric=get_classification_score(y_true=y_test,y_pred=y_test_pred)

         self.track_mlflow(best_model,classification_test_metric)

         preprocessor=load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
         model_dir_path=os.path.dirname(self.model_trainer_config.trained_model_file_path)
         os.makedirs(model_dir_path,exist_ok=True)

         Network_Model=NetworkModel(preprocessor=preprocessor,model=best_model)
         save_object(self.model_trainer_config.trained_model_file_path,obj=Network_Model)

         save_object("final_model/model.pkl",best_model)

         model_trainer_artifact= ModelTrainerArtifact(trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                              train_metric_artifact=classification_train_metric,
                              test_metric_artifact=classification_test_metric)
         logger.info("Model trainer artifact created")
         return model_trainer_artifact

        
    def initiate_model_trainer(self)->ModelTrainerArtifact:
        try:
            train_file_path=self.data_transformation_artifact.transformed_train_file_path
            test_file_path=self.data_transformation_artifact.transformed_test_file_path

            train_arr=load_numpy_array(train_file_path)
            test_arr=load_numpy_array(test_file_path)

            x_train,y_train,x_test,y_test=(
                train_arr[:,:-1],
                train_arr[:,-1],
                test_arr[:,:-1],
                test_arr[:,-1],
            )
            model=self.train_model(x_train,y_train,x_test,y_test)
            return model

        except Exception as e:
            raise NetworkSecurityException(e,sys)


