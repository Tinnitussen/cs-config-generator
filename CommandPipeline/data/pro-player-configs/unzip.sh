mkdir -p unzipped-configs
for f in *.zip; do
  name=$(basename "$f" .zip)
  unzip -j "$f" -d unzipped-configs
  inner=$(unzip -Z1 "$f")
  mv "unzipped-configs/$inner" "unzipped-configs/${name}.cfg"
done