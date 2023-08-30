resource "aws_amplify_app" "frontend" {
    name = "korrect" 
    repository = "https://github.com/data-dev-course/project4-team2"
    iam_service_role_arn = var.iam_service_role_arn
    oauth_token = var.GITHUB_TOKEN
    platform = "WEB"
    # Additional settings if necessary
    #auto_branch_creation_config {
    #    enable_auto_branch_creation = false
    #    #auto_branch_creation_patterns = [
    #    #  "feature/*",
    #    #  "hotfix/*"
    #    #]
    #}
}

resource "aws_amplify_branch" "frontend" {
    app_id = aws_amplify_app.frontend.id
    branch_name = "main"
    #base_directory = "app/services/frontend"
    stage = "PRODUCTION"
}

resource "aws_amplify_webhook" "frontend" {
    app_id = aws_amplify_app.frontend.id
    branch_name = aws_amplify_branch.frontend.branch_name
    description = "Webhook for main branch"
}