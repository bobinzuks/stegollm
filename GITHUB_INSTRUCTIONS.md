# Pushing to GitHub

Follow these steps to push the StegoLLM project to a public GitHub repository:

## Step 1: Create a new repository on GitHub

1. Go to [GitHub](https://github.com/) and sign in to your account
2. Click the "+" icon in the top right corner and select "New repository"
3. Enter a repository name (e.g., "stegollm")
4. Add a description: "A proxy app for compressing LLM prompts using steganography"
5. Keep the repository set to "Public"
6. Do NOT initialize the repository with a README, .gitignore, or license (we've already created these files locally)
7. Click "Create repository"

## Step 2: Connect your local repository to GitHub

Once your GitHub repository is created, you'll see instructions on the page. Use the option for "pushing an existing repository from the command line". Run these commands in your terminal:

```bash
# Replace YOUR_USERNAME with your actual GitHub username
git remote add origin https://github.com/YOUR_USERNAME/stegollm.git

# Push the local repository to GitHub
git push -u origin main
```

You'll be prompted to enter your GitHub username and password. If you have two-factor authentication enabled, you'll need to use a personal access token instead of your password.

## Step 3: Verify the repository is online

After pushing successfully, you can visit your GitHub repository in a web browser at:
```
https://github.com/YOUR_USERNAME/stegollm
```

## Step 4: Set up GitHub Pages (Optional)

To create a project website:

1. Go to your repository on GitHub
2. Click "Settings"
3. Scroll down to "GitHub Pages"
4. Under "Source", select "main" branch
5. Choose the "/docs" folder or "root" of the repository
6. Click "Save"

Your project will now be available at:
```
https://YOUR_USERNAME.github.io/stegollm/
```

## Additional Information

- You can update the remote URL to use SSH instead of HTTPS if you prefer:
  ```bash
  git remote set-url origin git@github.com:YOUR_USERNAME/stegollm.git
  ```

- If you want to create additional branches:
  ```bash
  git checkout -b feature/new-feature
  ```

- To update the repository after making changes:
  ```bash
  git add .
  git commit -m "Description of changes"
  git push