# frozen_string_literal: true

# Gives the navbar's social icons real labels.
#
# jekyll-socials builds each icon's tooltip from the _data/socials.yml key with
# `key.gsub('_', ' ').capitalize` and offers no way to configure it, so the icons
# read "Github username", "Orcid id", "Scholar userid", "Cv pdf". Wrap the tag and
# rewrite the labels it produced. Anything not listed here keeps the gem's label.
#
# The tooltip is also the accessible name of an icon-only link, so each anchor gets
# an `aria-label` as well -- `title` alone is not reliably announced by a screen
# reader, and there is no text inside the <a> to fall back to.
module SocialLinkLabels
  LABELS = {
    'cv_pdf' => 'CV (PDF)',
    'dblp_url' => 'DBLP',
    'email' => 'Email',
    'github_username' => 'GitHub',
    'linkedin_username' => 'LinkedIn',
    'orcid_id' => 'ORCID',
    'scholar_userid' => 'Google Scholar',
    'semanticscholar_id' => 'Semantic Scholar',
    'x_username' => 'X'
  }.freeze

  def render(context)
    html = super
    LABELS.each do |key, label|
      gem_label = key.gsub('_', ' ').capitalize
      html = html.gsub("title='#{gem_label}'", "title='#{label}' aria-label='#{label}'")
    end
    # Whatever the gem labelled and this map did not: still give it an aria-label.
    html.gsub(/title='([^']*)'(?! aria-label)/) { "title='#{$1}' aria-label='#{$1}'" }
  end
end

unless defined?(Jekyll::SocialLinksTag)
  raise "social_link_labels.rb: Jekyll::SocialLinksTag is gone -- did jekyll-socials " \
        "get dropped from `plugins:`/the Gemfile, or rename the tag class?"
end

Jekyll::SocialLinksTag.prepend(SocialLinkLabels)
