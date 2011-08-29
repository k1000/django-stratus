var editors = null;
$(document).ready( function(){
	// initialize from history
	//http://tkyk.github.com/jquery-history-plugin/#demos
	function loadContent(hash) {
	    if(hash != "") {
	        //pages.new_page( hash +".html" );
	    } else {
	    	
	    	
		}
	}
	// initialize pages
	
	var pages = new PageManager($("#pages"));
	var tabs = new TabManager($("ul.tabs"), pages);
	var pagae1 = $(".page").html();
	$(".page").remove();
	var editors = new EditorManager();
	var file_browser = new FileBrowserManager( tree_path );
    
    var loc = window.location.pathname;
	pages.new_page( loc, pagae1 );
	// give current page id
	//$(".page").attr("id", pages.mk_page_id( document.location.href ) );
	tabs.mk_tab( loc , $(".page h1").html() );
	//$.history.init(loadContent);

	var uploader = new qq.FileUploader({
	    // pass the dom node (ex. $(selector)[0] for jQuery users)
	    element: document.getElementById('id_file_upload'),
	    // get other data
	    params: { upload_dir: document.getElementById('id_upload_dir') },
	    // path to server-side upload script
	    action: UPLOAD_URL,
	    onComplete: function(id, fileName, data){
	    	alert( data );
	    	dispatch_form_respond(url, rel, data);
	    }
	}); 


	// ----------------- FILE BROWSER --------------------
	$("#toogle_files").click( function(event){
		event.preventDefault();
		$(this).removeClass("open").addClass("closed");
		$('#working_tree').toggle("fast");
	})

	// ----------------- NEW FILE --------------------
	$("#create_new_file").click( function(){
		var loc = document.getElementById("cur_path").value + "/" +
			document.getElementById("new_file_name").value;
		document.location = loc;
	})

	// ----------------- OPEN URL --------------------
	$("#open_preview").click( function(){
		var url = this.href;
		tabs.mk_tab(url, url );
		pages.hide_current();
		var tmp= $("#url_template").html().replace("sssss", url );
		var new_page = pages.new_page( url, tmp );
		return false
	});

	$('#content').delegate('.go', 'click', function(event) {
		var self = $(this);
		var src = self.prev().attr("value");
		self.parent().next().attr("src", src);
	});

	// ----------------- PAGES --------------------
	$(document).delegate('a.ajax', 'click', function(event) {
		dispatch_respond(this, this.pathname, this.rel, this.title )
		return false;
	});

	function dispatch_respond( self, url, rel, title) {
		//content
		if (rel == "contents" || rel == "edit" ) {
			// if its the same page do nothing
			if ( url != pages.current) {
				// hide current page
				pages.hide_current();
				//show if page is already loaded
				if ( pages.pages[url] ){
					tabs.activate_tab(url);
					pages.show_page(url);
				//open new page
				} else {
					tabs.mk_tab(url, title);
					if (rel == "edit" ) {
						pages.open_page( url, function(url, data){ 
							editors.mk( url );
						});
					} else {
						pages.open_page( url );
					}
				}				
			}
		//load in current page
		} else if (rel == "current" || rel == "prev" || rel == "next") {
			var current = $(self).parents(".page");
			get_page(url, current);
		//load in arbitrary container
		} else if (rel == "index" ) {
			file_browser.open( url );
		} else {
			get_page(url, $(rel));
		}
	}

	// ----------------- CONSOLE --------------------
	$("#console_enter").click(function( ){
		var data = {"com":"git status"};
		$('#console_output').load(CONSOLE_URL, data, function() {});
	})

	$("#console h4").click( function(){
		$("#console .content").toggle()
	})

	$("#console").draggable(function() {
		helper: "original" 
	});

	$("#console_enter").click( function(){
		return false
	})

	// ----------------- MESSAGES --------------------
	$("#messages a.close").click( function(){
		$("#messages").toggle();
		return false
	})

	function show_messages( msgs ){
		var msg_out = "";
		for (var i = msgs.length - 1; i >= 0; i--) {
			msg_out += "<li>" + msgs[i] + "</li>";
		};
		$("#messages ul").html( msg_out ).parent().toggle(true);
	}

	// ----------------- EDIT  --------------------
	$(document).delegate('form.ajax_editor button', 'click', function(event) {
		event.preventDefault();
		var self = $(this);
		var form = self.parents("form");
		var url = form.attr("action");
		editors.save(url);
		
		$.ajax({
			   type: "post",
			   url: url,
			   data: form.serialize(),
			   dataType: "json",
			   success: function(data){
			   		if ( data.msg ) {
			   			show_messages( data.msg );
			   		}
			   }
		});
	})

	// ----------------- FORMS --------------------
	$(document).delegate('form.ajax button', 'click', function(event) {
		event.preventDefault();
		var self = $(this);
		var form = self.parents("form");
		var url = form.attr("action");
		var rel = form.attr("rel");
		
		var to_upload = form.find("input[type=file]");
		// if there is file to upload
		if ( to_upload ) {

			if (to_upload[0].files.length) {
				// https://github.com/valums/file-uploader
				var uploader = new qq.FileUploader({
				    // pass the dom node (ex. $(selector)[0] for jQuery users)
				    element: to_upload[0],
				    // get other data
				    params: form.serializeArray(),
				    // path to server-side upload script
				    action: url,
				    onComplete: function(id, fileName, data){
				    	dispatch_form_respond(url, rel, data)
				    }
				}); 
			} else {
				show_messages( ["You must select file to upload"] );
			}
		} else {
			$.ajax({
				type: form.attr("method"),
				url: url,
				data: form.serialize(),
				dataType: "json",
				success: function(data){
					dispatch_form_respond(url, rel, data)
				}
			});
		}
	})
})

function dispatch_form_respond(url, rel, data){
	if ( data.msg ) {
		show_messages( data.msg );
	}
	if (  rel == "contents") {
		pages.hide_current();
		pages.new_page( url, data.html );
		var tab_text = $(data.html).find("h1").text().replace('"', "");
		tabs.mk_tab(url, tab_text);
	} else {
		$(rel).html( data.html );
	}
}

function get_prev_next( obj, current ) {
	// gets previous and next on both sides of current
	var prev_next = {"prev":null, "next":null};
	var var_prev = null;
	for (var key in obj){
		if (hasOwnProperty.call(obj, key)){
			if ( prev_next.prev ) {
				prev_next.next =  key;
				return prev_next
			}
			if ( key == current ) {
				prev_next.prev = var_prev;
			}
			var_prev = key;
		}
	}
	return prev_next
}

function get_page(url, rel){
	var rel = rel;
	var url = url; 
	$.get(url, function(data) {
		rel.html( data.html  )
	}, "json")
}

function FileBrowserManager( path ){
	this.container = $("#file_browser");
	this.current_path = path;

	get_page(path, this.container);

	this.refresh = function(){
		this.open( this.current_path );
	}

	this.open = function( url ){
		this.current_path = url;
		get_page(url, this.container);
	}
}


function TabManager( tab_container, pages ){
	this.tab_container = tab_container;
	this.pages = pages;
	this.current = previous = next = "";
	var self = this;

	tab_container.delegate("li", 'click', function(event){
		//event.preventDefault();
		var tab = $(this);
		var tab_url = tab.find("a.tab").attr("href");
		if (tab_url != self.pages.current) {
			self.deactivate_tabs();
			tab.addClass("active");
			self.pages.hide_current();
			self.pages.show_page(tab.find("a.tab").attr("href"));
		}
		return false
	});

	tab_container.delegate("a.close", 'click', function(event){
		//event.preventDefault();
		self.rm_tab($(this).next().attr("href"));
		return false;
	});

	this.get_tabs = function() {
		
	}
	this.mk_tab = function( url, title ){
		this.deactivate_tabs();
		return this.tab_container.append("<li class='active' ><a href='#' class='close' title='close' >x</a><a href='" + url + "' title=\""+ title +"\" class='tab' >" + title + "</a></li>")
	}
	this.rm_tab = function( url ){
		var tab_to_remove = this.get_tab_by_url( url ).parent()
		tab_to_remove.remove();
		var prev_next = get_prev_next( this.pages.pages, url );
		var new_active_tab = (prev_next.prev)? prev_next.prev: prev_next.next;
		this.pages.rm_page( url )
		if (new_active_tab){
			this.activate_tab( new_active_tab );
			this.pages.show_page( new_active_tab );
		}
	}
	this.deactivate_tabs = function( ){
		this.tab_container.find("li").removeClass("active");
	}
	this.get_tab_by_url = function( url ){
		return this.tab_container.find("a.[href='" + url +"']")
	}
	this.activate_tab = function( url ){
		this.deactivate_tabs();
		this.get_tab_by_url( url ).parent().addClass("active");
	}
}

function EditorManager( options ){
	this.editors = {};
	this.modes = [];
	this.mk = function( url, mode, options ){
		/*
		this.new_mode( mode, function() {
			//console.log( url )
			this.activate_editor( url, mode );
		});
		*/

		var text_area = $("form[action='"+ url +"'] textarea[name=file_source]");

		var mode = (mode)? mode : text_area.attr('class');
		
		var code_mirror = CodeMirror.fromTextArea( text_area[0], {
			mode: {name: mode},
			lineNumbers: true,
			indentUnit: 4
		});
		this.editors[url] = code_mirror;
	}
	this.save = function( url ){
		this.editors[url].save();
	}
	this.rm_editor = function( url ){
		delete this.editors[url];
	}
	this.new_mode = function( mode, callback ){
		for (var i = this.modes.length - 1; i >= 0; i--) {
			if (mode === this.modes[i]) 
			return callback()
		};
		if (mode){
			var url = STRATUS_MEDIA_URL +"stratus/CodeMirror-2.12/mode/" + mode + "/" + mode + ".js";
			loadScript( url, callback )		
		}

	}
}


function PageManager( page_container, options ){

	this.current = "";
	this.page_container = page_container;
	this.pages = {};
	this.transition = false;
	this.new_page = function( url, data ){
		var id = this.mk_page_id( url );
		this.pages[url] = id;
		this.set_current( url );
        //url = url.replace(/^.*#/, '');
        //$.history.load(url);
		this.page_container.append("<div class='page' id='" + id + "' >" + data + "</div>");
		return id
	}
	this.rm_page = function( url ){
		$("#"+this.get_page_id(url)).remove();
		delete this.pages[url]
	}
	this.mk_page_id = function( url ){
		return url.replace(/\//g, "_").replace(/\./g, "").replace(/:/g, "")
	}
	this.set_current = function( url ){
		this.current = url;
	}
	this.get_page_id = function( url ){
		return this.pages[url]
	}
	this.get_current_id = function( ){
		return this.pages[ this.current ]
	}
	this.get_page = function( url ){
		return $("#"+this.pages[ url ])
	}
	this.get_current = function( ){
		return $("#"+this.pages[ this.current ])
	}
	this.open_page = function( url, call_back ){
		var self = this;
		var url = url;
		var call_back = call_back;
		$.get(url, function(data) {
			self.new_page(url, data.html );
			if (call_back ) {
				call_back( url, data)
			}
		}, "json")
	}
	this.hide_current = function( ){
		var page = this.get_current( );
		this.transition = true;
		var self = this;
		return page.hide('slide', {direction: 'left'}, 700, function(){
			self.transition = false;
		});
	}
	this.show_page = function( url ){
		var page = this.get_page( url );
		this.set_current( url );
		page.show();
	}
}

// http://www.nczonline.net/blog/2009/07/28/the-best-way-to-load-external-javascript/
function loadScript(url, callback){

    var script = document.createElement("script")
    script.type = "text/javascript";

    if (script.readyState){  //IE
        script.onreadystatechange = function(){
            if (script.readyState == "loaded" ||
                    script.readyState == "complete"){
                script.onreadystatechange = null;
                callback();
            }
        };
    } else {  //Others
        script.onload = function(){
            callback();
        };
    }

    script.src = url;
    document.getElementsByTagName("head")[0].appendChild(script);
}