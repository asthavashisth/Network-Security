import os
import sys
import pandas as pd
from scipy.stats import ks_2samp

from networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logger
from networksecurity.utils.main_utils.utils import read_yaml_file, write_yaml_file
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH


class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self.schema_config = read_yaml_file(SCHEMA_FILE_PATH)

            if self.schema_config is None:
                raise ValueError("Schema config could not be loaded or is empty.")
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_number_of_columns(self, dataframe: pd.DataFrame) -> bool:
        try:
            expected_columns = self.schema_config["columns"]
            logger.info(f"Expected number of columns: {len(expected_columns)}")
            logger.info(f"Actual number of columns: {len(dataframe.columns)}")
            return len(dataframe.columns) == len(expected_columns)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_numerical_columns_exist(self, dataframe: pd.DataFrame) -> bool:
        try:
            required_columns = self.schema_config["numerical_columns"]
            return all(col in dataframe.columns for col in required_columns)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def detect_dataset_drift(self, base_df: pd.DataFrame, current_df: pd.DataFrame, threshold=0.05) -> bool:
        try:
            status = True
            report = {}

            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]
                test_result = ks_2samp(d1, d2)
                drift_detected = test_result.pvalue < threshold

                report[column] = {
                    "p_value": float(test_result.pvalue),
                    "drift_status": drift_detected
                }

                if drift_detected:
                    status = False

            drift_report_file_path = self.data_validation_config.drift_report_file_path
            os.makedirs(os.path.dirname(drift_report_file_path), exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path, content=report)

            return status
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            train_file_path = self.data_ingestion_artifact.trained_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            train_df = self.read_data(train_file_path)
            test_df = self.read_data(test_file_path)

            error_message = ""

            if not self.validate_number_of_columns(train_df):
                error_message += "Train file does not match schema column count.\n"

            if not self.validate_number_of_columns(test_df):
                error_message += "Test file does not match schema column count.\n"

            if not self.validate_numerical_columns_exist(train_df):
                error_message += "Train file missing numerical columns.\n"

            if not self.validate_numerical_columns_exist(test_df):
                error_message += "Test file missing numerical columns.\n"

            if error_message:
                raise Exception(error_message)

            drift_status = self.detect_dataset_drift(train_df, test_df)

            os.makedirs(os.path.dirname(self.data_validation_config.valid_train_file_path), exist_ok=True)

            train_df.to_csv(self.data_validation_config.valid_train_file_path, index=False, header=True)
            test_df.to_csv(self.data_validation_config.valid_test_file_path, index=False, header=True)

            return DataValidationArtifact(
                validation_status=drift_status,
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )

        except Exception as e:
            raise NetworkSecurityException(e, sys)
