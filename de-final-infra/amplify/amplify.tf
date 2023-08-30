resource "aws_amplify_app" "frontend" {
    name = "korrect"
    
    repository {
        repository_url = "https://github.com/data-dev-course/project4-team2"
        branch_name    = "main"
    }
    #iam_service_role_arn = local.iam_service_role_arn
    oauth_token = var.GITHUB_TOKEN

    # Additional settings if necessary
    auto_branch_creation_config {
        enable_auto_branch_creation = false
        #auto_branch_creation_patterns = [
        #  "feature/*",
        #  "hotfix/*"
        #]
    }
}

resource "aws_amplify_branch" "frontend" {
    app_id = aws_amplify_app.frontend.id
    branch_name = "main"
    base_directory = "app/services/frontend"
    # Environment variables for the build
    environment_variables {
        #ENV_KEY = "ENV_VALUE"
    }
}

resource "aws_amplify_webhook" "frontend" {
    app_id = aws_amplify_app.frontend.id
    branch_name = aws_amplify_branch.frontend.branch_name
    description = "Webhook for main branch"
}