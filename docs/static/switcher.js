(function() {
  'use strict';

  // Parses versions in URL segments like:
  // "3", "dev", "release/2.7" or "3.6rc2"
  var version_regexs = [
    '(?:\\d)',
    '(?:\\d\\.\\d[\\w\\d\\.]*)',
    '(?:dev)',
    '(?:release/\\d.\\d[\\x\\d\\.]*)'];

  var all_versions = {
    'dev': 'dev',
    '0.13': '0.13',
    '0.12c': '0.12c',
  };

  function build_version_select(current_version, current_release) {
    var buf = ['<select>'];

    $.each(all_versions, function(version, title) {
      buf.push('<option value="' + version + '"');
      if (version == current_version)
        buf.push(' selected="selected">' + current_release + '</option>');
      else
        buf.push('>' + title + '</option>');
    });

    buf.push('</select>');
    return buf.join('');
  }

  function navigate_to_first_existing(urls) {
    // Navigate to the first existing URL in urls.
    var url = urls.shift();
    if (urls.length == 0) {
      window.location.href = url;
      return;
    }
    $.ajax({
      url: url,
      success: function() {
        window.location.href = url;
      },
      error: function() {
        navigate_to_first_existing(urls);
      }
    });
  }

  function on_version_switch() {
    var selected_version = $(this).children('option:selected').attr('value') + '/';
    var url = window.location.href;
    var current_version = version_segment_in_url(url);
    var new_url = url.replace('/' + current_version,
                              '/' + selected_version);
    if (new_url != url) {
      navigate_to_first_existing([
        new_url,
        url.replace('/' + current_version,
                    '/' + selected_version)
				]);
    }
  }


  // Returns the path segment of the version as a string, like '3.6/'
  // or '' if not found.
  function version_segment_in_url(url) {
    var version_segment = '(?:(?:' + version_regexs.join('|') + ')/)';
    var version_regexp = '/(' + version_segment + ')';
    var match = url.match(version_regexp);
    if (match !== null)
      return match[1];
    return ''
  }

  $(document).ready(function() {
    var release = DOCUMENTATION_OPTIONS.VERSION;
    var version = release;
    var version_select = build_version_select(version, release);

    $('.version-placeholder').html(version_select);
    $('.version-placeholder select').bind('change', on_version_switch);
  });
})();

