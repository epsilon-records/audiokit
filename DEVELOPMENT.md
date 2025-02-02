## CI/CD Integration

The project uses GitHub Actions for CI/CD. The workflow:

1. Runs on push to main and pull requests
2. Tests against Python 3.12
3. Runs linting and formatting checks
4. Uploads test coverage to Codecov

To trigger a manual build:
1. Push to main branch
2. Create a pull request

## Pinecone Setup

1. Create a `.env` file in the project root
2. Add your Pinecone API key:
   ```
   PINECONE_API_KEY=your-api-key
   PINECONE_INDEX_NAME=audiokit-brain
   ```
3. Ensure the `.env` file is not committed to version control