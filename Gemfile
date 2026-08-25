source "https://rubygems.org"

# The github-pages gem pins the exact dependency versions GitHub Pages uses on
# its own build servers, so a local preview matches what actually gets deployed.
# It already bundles the three plugins declared in _config.yml
# (jekyll-include-cache, jekyll-sitemap, jekyll-seo-tag), so they are not
# repeated here -- declaring them separately invites version conflicts.
gem "github-pages", group: :jekyll_plugins

# Shipped with Ruby before 3.0 and removed from the standard library after,
# but `jekyll serve` still needs it.
gem "webrick", "~> 1.8"
