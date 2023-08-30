resource "aws_amplify_app" "frontend" {
    name = "korrect" 
    repository = "https://github.com/data-dev-course/project4-team2"
    iam_service_role_arn = var.iam_service_role_arn
    oauth_token = var.GITHUB_TOKEN
    platform = "WEB"
    custom_rule {
        source          = "</^[^.]+$|\\.(?!(css|gif|ico|jpg|js|png|txt|svg|woff|woff2|map|json)$)([^.]+$)/>"
        target          = "/index.html"
        status          = "200"
        condition       = null # This is optional, and since we're not using a condition, it's an empty string.
    }
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