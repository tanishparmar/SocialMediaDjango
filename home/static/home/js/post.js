$(document).ready(function () {
	// contents of the editor at any step
	var editorContent;
	var title, content, images;
	// language selected
	var languageSelected = "CPP";
	// editor-theme
	// var editorThemeSelected = "DARK";
	// indent-spaces
	var indentSpaces = 4;

	// HackerEarth API endpoints
	var RUN_URL = "run/";

	//Language Boilerplate Codes
	var langBoilerplate = {};
	langBoilerplate["C"] =
		"#include <stdio.h>\nint main(void) {\n	// your code goes here\n	return 0;\n}\n";
	langBoilerplate["CPP"] =
		"#include <iostream>\nusing namespace std;\n\nint main() {\n	// your code goes here\n	return 0;\n}\n";
	langBoilerplate["CSHARP"] =
		"using System;\n\npublic class Test\n{\n	public static void Main()\n	{\n		// your code goes here\n	}\n}\n";
	langBoilerplate["CSS"] = "/* begin writing below */";
	langBoilerplate["CLOJURE"] = "; your code goes here";
	langBoilerplate["HASKELL"] = "main = -- your code goes here";
	langBoilerplate["JAVA"] =
		"public class TestDriver {\n    public static void main(String[] args) {\n        // Your code goes here\n    }\n}";
	langBoilerplate["JAVASCRIPT"] =
		"importPackage(java.io);\nimportPackage(java.lang);\n\n// your code goes here\n";
	langBoilerplate["OBJECTIVEC"] =
		"#import <objc/objc.h>\n#import <objc/Object.h>\n#import <Foundation/Foundation.h>\n\n@implementation TestObj\nint main()\n{\n	// your code goes here\n	return 0;\n}\n@end";
	langBoilerplate["PERL"] = "#!/usr/bin/perl\n# your code goes here\n";
	langBoilerplate["PHP"] = "<?php\n\n// your code goes here\n";
	langBoilerplate["PYTHON"] =
		'def main():\n    # Your code goes here\n   return 0\n\nif __name__ == "__main__":\n    main()';
	langBoilerplate["R"] = "# your code goes here";
	langBoilerplate["RUBY"] = "# your code goes here";
	langBoilerplate["RUST"] =
		'fn main() {\n    // The statements here will be executed when the compiled binary is called\n\n    // Print text to the console\n    println!("Hello World!");\n}\n';
	langBoilerplate["SCALA"] =
		"object Main extends App {\n	// your code goes here\n}\n";

	// flag to block requests when a request is running
	var request_ongoing = false;

	// set base path of ace editor. Required by WhiteNoise
	ace.config.set("basePath", "/static/home/ace-builds/src/");
	// trigger extension
	ace.require("ace/ext/language_tools");
	// init the editor
	var editor = ace.edit("editor");

	// initial configuration of the editor
	editor.setTheme("ace/theme/twilight");
	editor.session.setMode("ace/mode/c_cpp");
	editor.getSession().setTabSize(indentSpaces);
	editorContent = editor.getValue();
	editor.setFontSize(15);
	// enable autocompletion and snippets
	editor.setOptions({
		enableBasicAutocompletion: true,
		enableSnippets: true,
		enableLiveAutocompletion: true,
	});
	// include boilerplate code for selected default language
	editor.setValue(langBoilerplate[languageSelected]);

	// create a simple selection status indicator
	var StatusBar = ace.require("ace/ext/statusbar").StatusBar;
	var statusBar = new StatusBar(
		editor,
		document.getElementById("editor-statusbar")
	);
	checkForInitialData();
	function checkForInitialData() {
		var code_content = document.getElementById("saved_code_content").value;
		var code_lang = document.getElementById("saved_code_lang").value;
		if (
			code_content != "" &&
			code_content != undefined &&
			code_content != null
		) {
			languageSelected = code_lang;
			$("option:selected")[0].selected = false;
			$("option[value='" + code_lang + "']")[0].selected = true;
			editor.setValue(code_content);
		}
	}
	function updateContent() {
		editorContent = editor.getValue();
		title = document.getElementById("title").value;
		content = document.getElementById("content").value;
		images = $("#images").prop("files");
	}
	function runCode() {
		// if a run request is ongoing
		if (request_ongoing) return;

		// hide previous compile/output results
		$(".output-response-box").hide();

		// disable button when this method is called
		$("#compile-code").prop("disabled", true);
		$("#run-code").prop("disabled", true);

		// take recent content of the editor for compiling
		updateContent();

		var csrf_token = $(":input[name='csrfmiddlewaretoken']").val();

		// if code_id present in url and update run URL
		// if (window.location.href.includes("code_id")) {
		// }

		request_ongoing = true;
		var run_data = new FormData();
		run_data.append("source", editorContent);
		run_data.append("lang", languageSelected);
		run_data.append("csrfmiddlewaretoken", csrf_token);
		run_data.append("title", title);
		run_data.append("content", content);
		if ($("#run-code").text().trim()=="Create"){
			RUN_URL="/create/"
		}
		else{
			RUN_URL="/edit/"
			run_data.append("user",document.getElementById("this_user").value);
			run_data.append("post_url",document.getElementById("post_url").value);
		}
		for (i = 0; i < images.length; i++) {
			run_data.append("image"+i,images[i])
		}
		// AJAX r	equest to Django for running code with input
		$.ajax({
			url: RUN_URL,
			type: "POST",
			data: run_data,
			enctype: "multipart/form-data",
			timeout: 10000,
			processData: false,
			contentType: false,
			success: function (response) {
				request_ongoing = false;

				// if(location.port == "")
				// 	$('#copy_code')[0].innerHTML = '<kbd>' + window.location.hostname + '/code_id=' + response.code_id + '/</kbd>';
				// else
				// 	$('#copy_code')[0].innerHTML = '<kbd>' + window.location.hostname + ':' +  location.port +'/code_id=' + response.code_id + '/</kbd>';

				$("#copy_code").css({ display: "initial" });

				// enable button when this method is called
				$("#compile-code").prop("disabled", false);
				$("#run-code").prop("disabled", false);

				// $("html, body")
				// 	.delay(500)
				// 	.animate(
				// 		{
				// 			scrollTop: $("#show-results").offset().top,
				// 		},
				// 		1000
				// 	);

				// $(".output-response-box").show();
				// $(".run-status").show();
				// $(".time-sec").show();
				// $(".memory-kb").show();

				// if (response.compile_status == "OK") {
				// 	if (response.run_status.status == "AC") {
				// 		$(".output-io").show();
				// 		$(".output-error-box").hide();
				// 		$(".output-io-info").show();
				// 		$(".compile-status")
				// 			.children(".value")
				// 			.html(response.compile_status);
				// 		$(".run-status")
				// 			.children(".value")
				// 			.html(response.run_status.status);
				// 		$(".time-sec")
				// 			.children(".value")
				// 			.html(response.run_status.time_used);
				// 		$(".memory-kb")
				// 			.children(".value")
				// 			.html(response.run_status.memory_used);
				// 		$(".output-o").html(response.run_status.output_html);
				// 		$(".output-i").html(input_given);
				// 	} else {
				// 		$(".output-io").show();
				// 		$(".output-io-info").hide();
				// 		$(".output-error-box").show();
				// 		$(".compile-status")
				// 			.children(".value")
				// 			.html(response.compile_status);
				// 		$(".run-status")
				// 			.children(".value")
				// 			.html(response.run_status.status);
				// 		$(".time-sec")
				// 			.children(".value")
				// 			.html(response.run_status.time_used);
				// 		$(".memory-kb")
				// 			.children(".value")
				// 			.html(response.run_status.memory_used);
				// 		$(".error-key").html("Run-time error (stderr)");
				// 		$(".error-message").html(response.run_status.stderr);
				// 	}
				// } else {
				// 	$(".output-io").show();
				// 	$(".output-io-info").hide();
				// 	$(".compile-status").children(".value").html("--");
				// 	$(".run-status").children(".value").html("Compilation Error");
				// 	$(".time-sec").children(".value").html("0.0");
				// 	$(".memory-kb").children(".value").html("0");
				// 	$(".error-key").html("Compile error");
				// 	$(".error-message").html(response.compile_status);
				// }
			},
			error: function (error) {
				request_ongoing = false;

				// enable button when this method is called
				$("#compile-code").prop("disabled", false);
				$("#run-code").prop("disabled", false);

				// $("html, body")
				// 	.delay(500)
				// 	.animate(
				// 		{
				// 			scrollTop: $("#show-results").offset().top,
				// 		},
				// 		1000
				// 	);

				// $(".output-response-box").show();
				// $(".run-status").show();
				// $(".time-sec").show();
				// $(".memory-kb").show();

				// $(".output-io").show();
				// $(".output-io-info").hide();
				// $(".compile-status").children(".value").html("--");
				// $(".run-status").children(".value").html("--");
				// $(".time-sec").children(".value").html("0.0");
				// $(".memory-kb").children(".value").html("0");
				// $(".error-key").html("Server error");
				// $(".error-message").html(
				// 	"Server couldn't complete request. Please try again!"
				// );
			},
		});
	}
	// when run-code is clicked
	$(".output-response-box").hide();
	$("#run-code").click(function () {
		runCode();
		window.location='/'
	});
	$("#lang").change(function(){

		languageSelected = $("#lang").val();

		// update the language (mode) for the editor
		if(languageSelected == "C" || languageSelected == "CPP"){
			editor.getSession().setMode("ace/mode/c_cpp");
		}
		else{
			editor.getSession().setMode("ace/mode/" + languageSelected.toLowerCase());
		}

		//Change the contents to the boilerplate code
		editor.setValue(langBoilerplate[languageSelected]);

	});
});
