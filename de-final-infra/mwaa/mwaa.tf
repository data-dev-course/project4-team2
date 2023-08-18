#-----------------------------------------------------------
# NOTE: MWAA Airflow environment takes minimum of 20 mins
#-----------------------------------------------------------
module "mwaa" {
  source = "../module/mwaa"

  name              = "de-3-2-mwaa-env"
  airflow_version   = "2.5.1"
  environment_class = "mw1.medium"
  create_s3_bucket  = false
  source_bucket_arn = "arn:aws:s3:::de-3-2"
  dag_s3_path       = "dags"

  ## If uploading requirements.txt or plugins, you can enable these via these options
  plugins_s3_path      = "mwaa_plugins/plugins.zip"
  requirements_s3_path = "mwaa_requirements/requirements.txt"

  logging_configuration = {
    dag_processing_logs = {
      enabled   = true
      log_level = "INFO"
    }

    scheduler_logs = {
      enabled   = true
      log_level = "INFO"
    }

    task_logs = {
      enabled   = true
      log_level = "INFO"
    }

    webserver_logs = {
      enabled   = true
      log_level = "INFO"
    }

    worker_logs = {
      enabled   = true
      log_level = "INFO"
    }
  }

  # airflow_configuration_options = {
  #   "core.load_default_connections" = "false"
  #   "core.load_examples"            = "false"
  #   "webserver.dag_default_view"    = "tree"
  #   "webserver.dag_orientation"     = "TB"
  # }

  min_workers        = 1
  max_workers        = 2
  vpc_id             = data.terraform_remote_state.vpc.outputs.vpc_id
  private_subnet_ids = data.terraform_remote_state.vpc.outputs.mwaa_private_subnets

  webserver_access_mode = "PUBLIC_ONLY"   # Choose the Private network option(PRIVATE_ONLY) if your Apache Airflow UI is only accessed within a corporate network, and you do not require access to public repositories for web server requirements installation
  source_cidr           = ["10.${data.terraform_remote_state.vpc.outputs.cidr_numeral}.0.0/16"] # Add your IP address to access Airflow UI

  tags = {
    name="de-3-2-airflow"
  }
}