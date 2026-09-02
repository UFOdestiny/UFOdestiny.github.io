source 'https://rubygems.org'

gem 'jekyll'

# Jekyll plugins that affect the build
group :jekyll_plugins do
    gem 'jekyll-3rd-party-libraries' # CDN libraries the theme pulls in
    gem 'jekyll-cache-bust'          # ?v=hash on assets
    gem 'jekyll-email-protect'       # `encode_email`, called by al_search's search-data template
    gem 'jekyll-imagemagick'         # responsive webp variants
    gem 'jekyll-link-attributes'     # rel/target on external links
    gem 'jekyll-minifier'            # minifies the built HTML/CSS/JS
    gem 'jekyll-regex-replace'
    gem 'jekyll-scholar'             # renders _bibliography/papers.bib
    gem 'jekyll-sitemap'             # /sitemap.xml
    gem 'jekyll-socials'             # the {% social_links %} tag
    gem 'jekyll-toc'                 # the post layout calls {% toc %} unconditionally
    gem 'jekyll-terser', :git => 'https://github.com/RobertoJBeltran/jekyll-terser.git'
    gem 'jemoji'
end

group :other_plugins do
    gem 'css_parser'
    gem 'observer' # used by jekyll-scholar
end

# al-folio theme runtime (versions pinned; upgrade with `bundle update`)
group :al_folio_plugins do
    gem 'al_folio_core', '= 1.0.15' # layouts, includes, styles
    gem 'al_icons', '= 1.0.0'       # icon sets
    gem 'al_folio_cv', '= 1.0.2'    # the /cv/ page from _data/cv.yml
    gem 'al_citations', '= 1.0.1'   # selected_papers.liquid calls its tag unconditionally
    gem 'al_img_tools', '= 1.0.3' # image zoom / lightbox
    gem 'al_search', '= 1.0.3'    # the navbar search box
end
