# 1. Run your scraper
python src/asynchscrapper.py

# 2. Update DVC tracking
dvc add data/
dvc push

# 3. Commit dataset metadata
git add data.dvc
git commit -m "Auto-update dataset"

# 4. Get the latest tag (if none exists, start at v1.0.0)
$lastTag = git tag --sort=-v:refname | Select-Object -First 1

if (-not $lastTag) {
    $newTag = "v1.0.0"
} else {
    # Remove the leading 'v'
    $version = $lastTag.TrimStart("v")

    # Split into MAJOR.MINOR.PATCH
    $parts = $version.Split(".")
    $major = [int]$parts[0]
    $minor = [int]$parts[1]
    $patch = [int]$parts[2]

    # Bump MINOR version for new data
    $minor += 1
    $patch = 0

    $newTag = "v$major.$minor.$patch"
}

# 5. Create the new tag
git tag -a $newTag -m "Auto dataset version $newTag"

Write-Host "Created dataset version: $newTag"
