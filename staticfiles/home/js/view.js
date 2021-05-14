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
	var COMPILE_URL = "compile/";
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
    editor.setReadOnly(true);
    $("#lang").change(function(){

		$("#lang").val(languageSelected);

	});
});