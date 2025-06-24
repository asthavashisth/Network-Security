from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logger
from networksecurity.entity.config_entity import DataIngestionConfig, DataValidationConfig
from networksecurity.entity.config_entity import TrainingPipelineConfig
import os
import sys


if __name__ == "__main__":
    try:
        trainingpipelineconfig= TrainingPipelineConfig()
        dataingestionconfig= DataIngestionConfig(trainingpipelineconfig)
        data_ingestion= DataIngestion(dataingestionconfig)
        logger.info("Initiated Data Ingestion Component")
        dataingestionartifact=data_ingestion.initiate_data_ingestion()
        logger.info("Data Ingestion Artifact Created")
        print(dataingestionartifact)
        data_validation_config=DataValidationConfig(trainingpipelineconfig)
        data_validation=DataValidation(dataingestionartifact,data_validation_config)
        logger.info("Initiated Data Validation Component")
        data_validation_artifact=data_validation.initiate_data_validation()
        logger.info("Data Validation Completed")
        print(data_validation_artifact)
        

    except Exception as e: 
        raise NetworkSecurityException(e,sys) 
