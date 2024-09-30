echo "Extracting Version information..."

# Get Target Directory

echo "Target Directory is $1"

# Locate pb file and extract version from its name

version=$(find $1 -type f -name 'swagger-prism-*-all.pb' | sed 's:.*/::'| cut -d "-" -f3)

echo "Detected version is $version"

# Write versions to version file

echo "api.version=$version"| tee $1/version.properties