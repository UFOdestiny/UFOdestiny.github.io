---
layout: page
permalink: /publications/
title: Publications
description: In reverse chronological order. Also on <a href='https://dblp.org/pid/31/2647-2.html'>DBLP</a>.
nav: true
nav_order: 1
---

{% include bib_search.liquid %}

{% comment %}
  jekyll-scholar renders each year group as a bare `<h2 class="bibliography">2026</h2>` with no id, and offers no config for one. So capture the bibliography, give the headings ids with the `regex_replace` filter (jekyll-regex-replace), then read the year list back out of the same string — splitting on the id marker leaves each year at the start of a chunk. That keeps the nav below in sync with the .bib for free, and the anchors are real HTML, so /publications/#2025 works without JavaScript. With JavaScript, the script after the nav stops the theme's filter from treating the year as a search term.
{% endcomment %}
{% capture bibliography %}{% bibliography %}{% endcapture %}
{% assign bibliography = bibliography | regex_replace: '<h2 class="bibliography">(\d+)</h2>', '<h2 class="bibliography" id="\1">\1</h2>' %}
{% assign year_chunks = bibliography | split: '<h2 class="bibliography" id="' %}

<style>
  /* Local to this page: the year nav and the scroll offset its anchors need, so `navbar_fixed: true` does not park a heading underneath the navbar. */
  .publication-years {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
  }
  .publication-years a {
    border: 1px solid var(--global-divider-color);
    border-radius: 4px;
    padding: 0.1rem 0.55rem;
    /* 1rem, like every other piece of reading text -- see the font-size floor in _sass/_local.scss. */
    font-size: 1rem;
    /* --local-year-color, from _sass/_local.scss: the theme's --global-text-color-light is only 3.8:1 on white, below 4.5:1 for 1rem text. */
    color: var(--local-year-color);
  }
  .publication-years a:hover {
    border-color: var(--global-theme-color);
    color: var(--global-theme-color);
  }
  .publications h2.bibliography,
  .publications li .row > div[id] {
    scroll-margin-top: 5rem;
  }
</style>

<nav class="publication-years" aria-label="Jump to year">
  {% for chunk in year_chunks offset: 1 %}
    {% assign year = chunk | split: '"' | first %}
    <a href="#{{ year }}">{{ year }}</a>
  {% endfor %}
</nav>

<script>
  /* The theme's bibsearch.js copies the URL hash into the filter box, so `#2021` filtered the list to every entry whose text contains "2021" (an abstract mentioning "April 2021" included) instead of jumping to that year. For a hash that names a year heading, clear the filter and scroll to the heading; any other hash, such as the home page's /publications/#citekey links, keeps the theme's filter. setTimeout makes this run after bibsearch.js's own DOMContentLoaded and hashchange handlers. */
  (function () {
    function showYear() {
      var year = decodeURIComponent(window.location.hash.slice(1));
      var heading = /^\d{4}$/.test(year) && document.getElementById(year);
      var input = document.getElementById("bibsearch");
      if (!heading || !input) return;
      input.value = "";
      input.dispatchEvent(new Event("input"));
      heading.scrollIntoView();
    }
    function later() {
      setTimeout(showYear, 0);
    }
    document.addEventListener("DOMContentLoaded", later);
    window.addEventListener("hashchange", later);
  })();
</script>

<div class="publications">

{{ bibliography }}

</div>
