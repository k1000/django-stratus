var editors = null;

$(document).ready( function(){
	// initialize from history
	//http://tkyk.github.com/jquery-history-plugin/#demos

	// initialize pages
	var pages = new PageManager($("#pages"));
	var tabs = new TabManager($("ul.tabs"), pages);
	var pagae1 = $(".page").html();
	$(".page").remove();
	var editors = new EditorManager();
	var loc = window.location.pathname;

	pages.new_page( loc, $(".page h2").html() ,pagae1 );

	if(window.tree_path){
		var file_browser = new FileBrowserManager( tree_path );
	}

	// --------------- MESSAGE EVENTS --------------------
	$(document).bind('page_created', function(e, data, page) {
	    ws.send( {msg:"page "+ data.url + " opened", nick:USER_NAME, room:REPO, type:"info" });
	} );
	$(document).bind('page_edit', function(e, data, page) { 
		ws.send( {msg:"page "+ data.url + " edited", nick:USER_NAME, room:REPO, type:"info" });
	} );

	// ------------------- TOGGLE --------------------
	$(".toggle").click( function(event){
		event.preventDefault();
		if ( this.rel ){
			$(this.rel).toggle("fast");
		} else {
			$(this).next().toggle("fast");
		}
	})

	// ------------------    NEW FILE --------------------
	$("#create_new_file").click( function(e){
		e.preventDefault()
		var dir = (file_browser.current_dir)? file_browser.current_dir + "/" : "";
		var url = NEW_FILE_URL
			+ dir
			+ document.getElementById("new_file_name").value;
		//pages.hide_current();
		//tabs.mk_tab(url, "new file "+ url );
		pages.open_page( url, "new file "+ url, function(url, data){ 
			editors.mk( url );
		});
	})

	// ----------------- NEW FOLDER --------------------
	$("#create_new_folder").click( function(e){
		e.preventDefault();
		var dir = (file_browser.current_dir)? file_browser.current_dir + "/" : "";
		var url = NEW_FOLDER_URL
			+ dir
			+ document.getElementById("new_folder_name").value;
		get_ajax(url, "#messages");
	})

	// ----------------- OPEN PREVIEW --------------------
	$("#open_preview").click( function(){
		var url = this.href;
		var tmp= $("#url_template").html().replace("sssss", url );
		var new_page = pages.new_page( url, url, tmp );
		return false
	});

	// ----------------- OPEN URL --------------------
	$('#content').delegate('.go', 'click', function(event) {
		var self = $(this);
		var src = self.prev().attr("value");
		self.parent().next().attr("src", src);
	});

	// ----------------- OPEN PAGES --------------------
	$(document).delegate('a.ajax', 'click', function(event) {
		
		var path = this.pathname;
		var path_get = this.href.split("?")
		if (path_get.length > 1) {
			path += "?" + path_get[1];
		}
		dispatch_respond(this, path, this.rel, this.title )
		return false;
	});

	function dispatch_respond( self, url, rel, title) {
		//content
		if (rel == "contents" || rel == "edit" ) {
			// if its the same page do nothing
			if ( url != pages.current) {
				// hide current page
				
				//show if page is already loaded
				if ( pages.pages[url] ){
					//tabs.activate_tab(url);
					pages.show_page(url);
				//open new page
				} else {
					if (rel == "edit" ) {
						pages.open_page( url, title, function(url, data, page){ 
							editors.mk( url, page );
						});
					} else {
						pages.open_page( url, title );
					}
				}				
			}
		//load in current page
		} else if (rel == "current" || rel == "prev" || rel == "next") {
			var current = $(self).parents(".page");
			get_ajax(url, current);
		//syncronize file browser
		} else if (rel == "index" ) {
			file_browser.open( url );
		//load in arbitrary container
		} else {
			get_ajax(url, $(rel));
		}
	}

	// ----------------- COMMANDS --------------------
	function reload_window( data ) { location.reload(true) };

	var git_commands = {
		git_status: { str:"git status" },
		create_branch: { str:"git checkout -b {{name}}", param:["name"], callback:reload_window },
		activate_branch: { str:"git checkout {{name}}", param:["name"], callback:reload_window },
		delete_branch: { str:"git branch -D {{name}}", param:["name"], callback:reload_window }
	}

	$(document).delegate('.cmd', 'click', function(event) {
		event.preventDefault()
		var command = git_commands[this.name];
		var cmd = command.str;
		var repo = this.getAttribute("data-repo");
		if (command.param){
			var param_len = command.param.length;
			var input_param = $(this).parent().find("input[name=param]").val().split(" ");
			var input_param_len = input_param.length;
			if ( param_len != input_param_len ) {
				show_messages( this.name + " expects " + input_param_len + " parameter " + command.param.join(" ") )
				return False
			}
			for (var i = command.param.length - 1; i >= 0; i--) {
				var to_replece = "{{" + command.param[i] + "}}";
				cmd = cmd.replace(to_replece, input_param[i]);
			};
		}
		git_command( repo, cmd, command.callback );
		return false
	})

	// ----------------- CONSOLE --------------------
	$("#console_enter").click(function( ){
		var cmd = $("#console-input").val();
		$('#console_output').append( "<p>$ "+ cmd +"</p>" );
		git_command( REPO, cmd, function( data ) {
			$('#console_output').append( "<pre>"+ data + "</pre>" );
		})
	})

	$("#console > p").click( function(){
		$("#console .content").toggle()
	})

	$("#console").draggable( {
		containment : $('#console'),
  		handle      : $('#console > p')
		//helper: "original" 
	});

	function git_command( repo, cmd, callback ){
		var callback = callback;
		var send_data = {
			"com": cmd,
			"csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val()
		};
		var console_url = BASE_URL + repo + "/consol/";
		$.post(
			console_url, 
			send_data,
			function(data) {
				if (callback) {
					callback(data);
				} else {
					show_messages(["<pre>"+ data +"</pre>"]);
				}
			},
			"html"
		)
	}

	// ----------------- MESSAGES --------------------
	$("#messages a.close").click( function(){
		$("#messages").toggle();
		return false
	})

	// -------------------- EDIT  --------------------
	

	// ----------------- FORMS --------------------
	$(document).delegate('form.ajax button', 'click', function(event) {
		event.preventDefault();
		var self = $(this);
		var form = self.parents("form");
		var url = form.attr("action");
		var rel = form.attr("rel");
		var to_upload = form.find("input[type=file]");

		$.ajax({
				type: form.attr("method"),
				url: url,
				data: form.serialize(),
				dataType: "json",
				success: function(data){
					dispatch_form_respond(url, rel, data)
				}
		});

		// if there is file to upload
		/*if ( to_upload ) {

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
			
		}*/
	})

	function dispatch_form_respond(url, rel, data){
		if ( data.msg ) {
			show_messages( data.msg );
		}
		if ( rel == "contents" ) {
			var tab_text = $(data.html).find("h1").text().replace('"', "");
			tabs.mk_tab(url, tab_text);
			pages.new_page( url, tab_text, data.html );
		} else if ( rel == "edit" ) {
			var tab_text = $(data.html).find("h1").text().replace('"', "");
			pages.open_page( url, tab_text, function(url, data, page){ 
				editors.mk( url, page );
				this.page_container.trigger("page_edit", { "url":url });
			});
			
			//tabs.mk_tab(url, tab_text);
		} else {
			$(rel).html( data.html );
		}
	}
})

function show_messages( msgs ){
	var msg_out = "";
	for (var i = msgs.length - 1; i >= 0; i--) {
		msg_out += "<li>" + msgs[i] + "</li>";
	};
	$("#messages ul").html( msg_out ).parent().toggle(true);
}

function get_prev_next( obj, current ) {
	// gets previous and next on both sides of current
	var prev_next = {"prev":null, "next":null};
	var var_prev = null;
	var current_found = false;

	for (var key in obj){
		if (hasOwnProperty.call(obj, key)){
			if ( prev_next.prev || current_found) {
				prev_next.next =  key;
				return prev_next
			}
			if ( key == current ) {
				prev_next.prev = var_prev;
				current_found = true;
			}
			var_prev = key;
		}
	}
	return prev_next
}

function get_ajax(url, rel, callback){
	var rel = rel;
	var url = url; 
	var callback = callback; 
	$.get(url, function(data) {
		rel.html( data.html  )
		if ( callback) callback(url, rel, data);
		if ( data.msg ) show_messages( data.msg );
		if ( data.reload_fbrowser ) file_browser.refresh();
	}, "json")
}

function FileBrowserManager( path ){
	this.container = $("#file_browser");
	this.current_path = path;
	this.current_dir = "";
	// http://valums.com/ajax-upload/

	get_ajax(path, this.container);

	this.set_uploader = function( dir ){
		var dir = dir;
		var self = this;
		this.uploader = new qq.FileUploader({
		    // pass the dom node (ex. $(selector)[0] for jQuery users)
		    element: document.getElementById('id_file_upload'),
		    // get other data
		    params: { 
			    upload_dir: dir
		   	},
		    // path to server-side upload script
		    action: UPLOAD_URL,
		    onComplete: function(id, fileName, data){
		    	show_messages( data.msg );
		    	self.refresh();
		    }
		}); 
	}

	this.set_uploader( this.current_dir )

	this.refresh = function(){
		this.open( this.current_path );
	}

	this.open = function( url ){
		var self = this;
		this.current_path = url;
		get_ajax(url, this.container, function(url, rel, data){
			var dir = data.path
			if ( dir != self.current_dir ){
				self.current_dir = dir;
				self.set_uploader( dir );
			}
		});
	}
}


function TabManager( tab_container, pages ){
	this.tab_container = tab_container;
	this.pages = pages;
	this.pages.tabber = this;
	this.current = previous = next = "";
	var self = this;

	tab_container.delegate("li", 'click', function(event){
		//event.preventDefault();
		var tab = $(this);
		var tab_url = tab.find("a.tab").attr("href");
		if (tab_url != self.pages.current) {
			self.deactivate_tabs();
			tab.addClass("active");
			//self.pages.hide_current();
			self.pages.show_page(tab.find("a.tab").attr("href"));
		}
		return false
	});

	tab_container.delegate("a.close", 'click', function(event){
		//event.preventDefault();
		self.rm_tab($(this).next().attr("href"));
		return false;
	});

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
	
	this.connect = function( page ){
	    var editor = this;
    	page.delegate('form.ajax_editor .button', 'click', function(event) {
    		event.preventDefault();
    		var self = $(this);
    		var form = self.parents("form");
    		var url = form.attr("action");
    		editor.save(url);
		
    		$.ajax({
    			type: "post",
    			url: url,
    			data: form.serialize(),
    			dataType: "json",
    			success: function(data){
    				if ( data.msg ) show_messages( data.msg );
    			}
    		});
    	})
    }
	
	this.mk = function( url, page, mode, options ){

		var text_area = page.find("textarea[name=file_source]");
		
		if (text_area.length > 0){
			/*
			this.new_mode( mode, function() {
				//console.log( url )
				this.activate_editor( url, mode );
			});
			*/
			text_area.trigger("edit", {url:url});
			var mode = (mode)? mode : text_area.attr('class');
			var code_mirror = CodeMirror.fromTextArea( text_area[0], {
				mode: {name: mode},
				lineNumbers: true,
				indentUnit: 4
			});
			this.editors[url] = code_mirror;
			this.connect( page )
		}
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
	this.tabber = null;

	this.new_page = function( url, title, data ){
		// creates page from data and returns it
		var id = this.mk_page_id( url );
		this.set_current( url );
		this.tabber.mk_tab(url, title );

		var new_page = $("<div class='page' id='" + id + "' >" + data + "</div>").appendTo(this.page_container);
		this.page_container.trigger("page_created", {'sender': new_page, "url":url });
		this.pages[url] = new_page;
		return new_page
	}
	this.rm_page = function( url ){
		this.pages[url].remove();
		delete this.pages[url]
	}
	this.mk_page_id = function( url ){
		return url.replace(/\//g, "_").replace(/\./g, "").replace(/:/g, "")
	}
	this.set_current = function( url ){
		this.page_container.trigger("current_page", {url:url})
		this.current = url;
	}
	this.get_page = function( url ){
		// returns page content by its url
		return this.pages[url]
	}
	this.get_current = function( ){
		// returns current page
		return this.pages[ this.current ]
	}
	this.open_page = function( url, title, call_back ){
		// opens page from url
		var self = this;
		var url = url;
		var call_back = call_back;
		//this.tabber.mk_tab( url, title );
		this.hide_current();
		$.get(url, function(data) {
			var page = self.new_page(url, title, data.html );
			if (call_back ) {
				call_back( url, data, page)
			}
		}, "json")
	}
	this.hide_current = function( ){
		var page = this.get_current();
		this.transition = true;
		var self = this;
		return page.hide('slide', {direction: 'left'}, 700, function(){
			self.transition = false;
		});
	}
	this.show_page = function( url ){
		this.tabber.activate_tab(url);
		this.hide_current();
		var page = this.get_page( url ).show();
		this.set_current( url );
	}
}



function str_replace( text, replacer ){
	// replace {{ in string }}

	for (replace in replacer) {
		text = text.replace("{{"+replace+"}}", replacer[replace]);
	};
	return text
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

