# Drops theme assets that no page on this site can request.
#
# `exclude:` in _config.yml cannot do this: Jekyll's theme-assets reader walks the
# gem's assets/ directory directly and never consults the exclude list, so every
# stylesheet and script al_folio_core ships lands in _site whether a template asks
# for it or not. The files below back features this site does not have — Jupyter
# notebook posts, typograms, `page.pretty_table`, tabs, masonry, calendars — and
# together they are ~350 KB of the build output.
#
# Nothing here is loaded conditionally at runtime, so removing them cannot break a
# page: verify with a build diff after a theme upgrade, when a new template could
# start requesting one of them.
PRUNED_THEME_ASSETS = %w[
  assets/css/jupyter.css
  assets/css/jupyter-grade3.css
  assets/css/jupyter-monokai.css
  assets/js/calendar-setup.js
  assets/js/masonry.js
  assets/js/table-engine.js
  assets/js/tabs.js
  assets/js/typograms.js
].freeze

Jekyll::Hooks.register :site, :post_read do |site|
  site.static_files.reject! do |file|
    PRUNED_THEME_ASSETS.include?(file.relative_path.sub(%r{\A/}, ""))
  end
end
