## CI/CD Integration

The project uses GitHub Actions for CI/CD. The workflow:

1. Runs on push to main and pull requests
2. Tests against Python 3.11
3. Runs linting and formatting checks
4. Uploads test coverage to Codecov

To trigger a manual build:
1. Push to main branch
2. Create a pull request 