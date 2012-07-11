import traceback
import nose
import os
from nose.plugins import Plugin

def split_name(name, upper_first=True, upper_after_underscore=True):
    upper_first = True
    title = []
    for ch in name:
        if ch.isupper() and not upper_first:
            title.append(' ')
        if upper_first:
            ch = ch.upper()
            upper_first = False
        if ch == '_' or ch == '.':
            ch = ' '
            upper_first = upper_after_underscore
        title.append(ch)
    return ''.join(title)
    
class ReqsOutput(Plugin):
    """
    Output test results in a format suitable for Komodo's unit-testing
    framework.
    """
    # Required attributes:
    
    name = 'reqs'   # invoke with --with-reqs argument to Nose
    enabled = True
    #score = 2 # run late
    
    def __init__(self):
        super(ReqsOutput, self).__init__()
        self.headers = [ '<html><head>',
                      '<title>Test output</title>',
                      '<link href="http://github.cerner.com/pages/Axiom/axiom_base/assets/css/axiom.css" rel="stylesheet" id="axiomCSS">',
                      '<style type="text/css">.filename{margin: 5px;}.hidden{display:none;}fieldset { padding: 1px 0 15px 10px; border: 1px solid lightGray; } legend { padding: 2px; width: inherit; border-style: none; margin-bottom: 0;}',
                      '.ok { color: green; } .error, .fail { color: red; }'
                      '</style>'
                      '<script src="http://code.jquery.com/jquery-latest.min.js" type="text/javascript"></script>'
                      '<script type="text/javascript">',
                      '$(function(){$(document).on("click","a", function (){$("#" + $(this).data("control")).toggle();});',
                      '$(document).on("click", "#expandAll",function(){$(":hidden").show();})'
                      '});'
                      '</script>',
                      '</head><body>',
                      '<h1>Test Output</h1>',
                      '<p>Test are grouped by Python modules and class. The numbering is just and ordered list and will change as tests are added or removed. <a id="expandAll">+ Expand All Sections</a></p>', ]
        self.toc = []
        self.html = []
    
    
    def options(self, parser, env=os.environ):
        parser.add_option('--requirements-file',
                          help="The full name of the generated requirements file (Default is requirements.html).")        
        parser.add_option('--nested-requirements', action="store_true", dest="nested", default=False,
                          help="To nest the requirements accordingly.")

    def configure(self, options, conf):
        super(ReqsOutput, self).configure(options, conf)
        if options.requirements_file:
            self.output_file = options.requirements_file
        else:
            self.output_file = 'requirements.html'
        
        self.nested = options.nested
        self.last_path = None
            
    def addSuccess(self, test, capt):
        self.html.append('<span class="ok">OK</span> ')
        
    def addError(self, test, err, capt):
        self.error = self.formatErr(err)
        self.html.append('<span class="error">ERROR</span> ')
            
    def addFailure(self, test, err, capt, tb_info):
        self.error = self.formatErr(err)
        self.html.append('<span class="fail">FAIL</span> ')

    def finalize(self, result):
        self.headers.append('<div>')
        if not result.wasSuccessful():
            self.headers.extend(['<span class="fail">FAILED ( ',
                              'failures=%d ' % len(result.failures),
                              'errors=%d' % len(result.errors),
                              ')</span>'])                             
        else:
            self.headers.append('<span class="ok">OK</span>')
        self.headers.append('</div>')
        self.headers.append('<div>')
        self.headers.append("Ran %d test%s" %
                         (result.testsRun, result.testsRun != 1 and "s" or ""))
        self.headers.append('</div>')
        self.html.append('</body></html>')
        # print >> sys.stderr, self.html
        f = open(self.output_file, 'w')
        
        # Write a TOC
        for l in self.headers:
            f.write(l)
        for l in self.html:
            f.write(l)
            #self.stream.writeln(l)
        f.close()
        
    def formatErr(self, err):
        exctype, value, tb = err
        return ''.join(traceback.format_exception(exctype, value, tb))
    
    def setOutputStream(self, stream):
        # grab for own use
        self.stream = stream
        self.depth = 0
        self.modules = []

    def startContext(self, ctx):
        try:
            n = ctx.__name__
        except AttributeError:
            n = str(ctx).replace('<', '').replace('>', '')
        self.depth += 1
        self.toc.append(n)
        self.test_count = 0
        ul = 'ul' + n
        style = ''
        plus = ''
        if isinstance(ctx, type):
            style = 'hidden'
            plus = '+/-  '

        # Check if nesting is enabled or not
        if self.nested or isinstance(ctx, type):
            self.html.extend(['<fieldset>', '<legend><a data-control="{0}">{1}'.format(ul, plus), 
                split_name(n), '</a></legend>','<div id="{0}" class="{1}">'.format(ul, style)])

        # Want the 'last_path' to be inside the collapsable div
        if self.last_path and '__init__' not in self.last_path:
            self.html.extend(['<div class="filename"><em>Filename: </em>', self.last_path, '</div>'])

        try:
            path = ctx.__file__.replace('.pyc', '.py')
            self.last_path = path
        except AttributeError:
            self.last_path = None
            pass

        # Start the ordered list
        if self.nested or isinstance(ctx, type):
            self.html.extend(['<ol>'])


    def stopContext(self, ctx):
        #if isinstance(ctx, type):
        self.html.extend(['</ol>', '</div>', '</fieldset>'])
        self.test_count = 0
        self.depth -= 1
    
    def startTest(self, test):
        self.error = None # Reset error
        self.test_count += 1
        self.html.extend([ '<li>'])
                
    def stopTest(self, test):
        self.html.extend([ '<span>',
                    test._testMethodDoc or 'No Requirement Listed for ' + str(test),
                    '</span>' ])
        if self.error:
            self.html.append('<pre>%s</pre>' % self.error)
        self.html.append('</li>')
        