/* Autocomplete Widget
 */
Faceted.AutocompleteWidget = function (wid) {
    var self = this;
    this.wid = wid;
    this.widget = jQuery("#" + wid + "_widget");
    this.widget.show();
    this.title = jQuery("legend", this.widget).html();
    this.elements = this.widget.find("option");
    this.select = jQuery("#" + this.wid);
    this.multiple = this.widget.data("multiple") ? true : false;
    this.placeholder = this.widget.data("placeholder");
    this.autocomplete_view = this.widget.data("autocomplete-view");
    this.selected = [];
    this.button = jQuery("input[type=submit]", this.widget);

    this.select.select2({
        placeholder: this.placeholder,
        multiple: this.multiple,
        allowClear: true,
        minimumInputLength: 2,
        ajax: {
            url: this.autocomplete_view,
            delay: 250,
            dataType: "json",
            params: {
                global: false,
            },
            data: function (term) {
                return {
                    term: term,
                    add_terms: true,
                };
            },
            results: function (data) {
                return {
                    results: data,
                };
            },
            cache: false,
        },
    });

    // Handle text change
    jQuery("form", this.widget).on("submit", function () {
        return false;
    });

    if (this.button.length) {
        this.button.on("click", function () {
            self.text_change(self.button);
        });
    } else {
        this.select.on("select2-close", function (evt) {
            self.select_change(this, evt);
        });

        this.select.on("select2-removed", function (evt) {
            self.select_change(this, evt);
        });
    }

    // Default value
    var value = this.select.select2("val");
    if (value) {
        this.selected = [this.select];
        if (this.multiple) {
            Faceted.Query[this.wid] = value;
        } else {
            Faceted.Query[this.wid] = [value];
        }
    }

    // Bind events
    jQuery(Faceted.Events).on(Faceted.Events.QUERY_CHANGED, function () {
        self.synchronize();
    });
    jQuery(Faceted.Events).on(Faceted.Events.RESET, function () {
        self.reset();
    });
};

Faceted.AutocompleteWidget.prototype = {
    // Selections are stored in Faceted.Query (and the URL) as JSON encoded
    // {id, text} objects, so the label survives a page reload.
    encode: function (item) {
        return JSON.stringify({ id: item.id, text: item.text });
    },

    // Decode a stored value. Plain values (free text, defaults, URLs saved
    // before selections were JSON encoded) are used as both id and text.
    decode: function (raw) {
        var val = null;
        try {
            val = JSON.parse(raw);
        } catch {
            val = null;
        }
        if (val === null || typeof val !== "object" || val.id === undefined) {
            return { id: String(raw), text: String(raw) };
        }
        var text = val.text === undefined || val.text === null ? val.id : val.text;
        return { id: String(val.id), text: String(text) };
    },

    select_change: function (element) {
        if (!jQuery(element).val()) {
            element = null;
        }
        this.do_query(element);
    },

    text_change: function (element) {
        this.do_query(element);
        jQuery(element).removeClass("submitting");
    },

    do_query: function (element) {
        var self = this;
        var data = this.select.select2("data");
        var value = [];
        if (data && !Array.isArray(data)) {
            data = [data];
        }
        jQuery.each(data || [], function (idx, item) {
            value.push(self.encode(item));
        });

        if (!element) {
            this.selected = [];
            return Faceted.Form.do_query(this.wid, []);
        }
        this.selected = [this.select];

        var where = jQuery("input[type=radio]:checked", this.widget);
        where = where.length == 1 ? where.val() : "all";
        if (where == "all") {
            return Faceted.Form.do_query(this.wid, value);
        }

        var current = Faceted.Query[this.wid] || [];
        var current_ids = current.map(function (raw) {
            return self.decode(raw).id;
        });
        jQuery.each(value, function (idx, val) {
            if (!current_ids.includes(self.decode(val).id)) {
                current.push(val);
            }
        });
        return Faceted.Form.do_query(this.wid, current);
    },

    reset: function () {
        this.selected = [];
        this.widget.removeClass("faceted-widget-active");
        this.select.select2("val", null);
    },

    synchronize: function () {
        var self = this;
        var value = Faceted.Query[this.wid];
        if (!value) {
            return this.reset();
        }

        if (!Array.isArray(value)) {
            value = [value];
        }

        var data = [];
        jQuery.each(value, function (idx, raw_val) {
            var item = self.decode(raw_val);
            if (self.multiple) {
                data.push(item);
            } else {
                data = item;
            }
        });

        this.select.select2("data", data);
        this.selected = [this.select];
        this.widget.addClass("faceted-widget-active");
    },

    criteria: function () {
        var html = [];
        var title = this.criteria_title();
        var body = this.criteria_body();
        if (title) {
            html.push(title);
        }
        if (body) {
            html.push(body);
        }
        return html;
    },

    criteria_title: function () {
        if (!this.selected.length) {
            return "";
        }

        var link = jQuery('<a href="#" class="faceted-remove">remove</a>');
        link.attr("id", "criteria_" + this.wid);
        link.attr("title", "Remove " + this.title + " filters");
        var widget = this;
        link.on("click", function () {
            widget.criteria_remove();
            return false;
        });

        var html = jQuery("<dt>");
        html.attr("id", "criteria_" + this.wid + "_label");
        html.append(link);
        html.append("<span>" + this.title + "</span>");
        return html;
    },

    criteria_body: function () {
        if (!this.selected.length) {
            return "";
        }

        var widget = this;
        var html = jQuery("<dd>");
        var elements = Faceted.Query[this.wid];
        elements = elements ? elements : [];
        jQuery.each(elements, function () {
            var raw = this.toString();
            var item = widget.decode(raw);
            var label = item.text;
            if (raw.length > 0) {
                var span = jQuery('<span class="faceted-autocomplete-criterion">');
                var link = jQuery('<a href="#" class="faceted-remove">remove</a>');
                link.attr("id", "criteria_" + widget.wid + "_" + item.id);
                link.attr("title", "Remove " + label + " filter");
                link.on("click", function () {
                    widget.criteria_remove(raw);
                    return false;
                });
                span.append(link);
                jQuery("<span>").text(label).appendTo(span);
                html.append(span);
            }
        });
        return html;
    },

    criteria_remove: function (value) {
        if (!value) {
            this.reset();
            return this.do_query();
        }

        var current = Faceted.Query[this.wid] || [];
        Faceted.Query[this.wid] = current.filter(function (item) {
            return item != value;
        });

        this.synchronize();
        this.do_query(this.select);
    },
};

Faceted.initializeAutocompleteWidget = function () {
    jQuery("div.faceted-autocomplete-widget").each(function () {
        var wid = jQuery(this).attr("id");
        wid = wid.split("_")[0];
        Faceted.Widgets[wid] = new Faceted.AutocompleteWidget(wid);
    });
};

// Initialize
jQuery(Faceted.Events).on(
    Faceted.Events.INITIALIZE,
    Faceted.initializeAutocompleteWidget
);
