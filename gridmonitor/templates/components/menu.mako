<%def name="top_nav(nav_items,active)">
  <ul id="navlist">
    % for slide, link in nav_items:
      % if slide == active:
        <li class="active"><a href=${link} class="active">${slide}</a></li>\
      % else:
       <li><a href=${link}>${slide}</a></li>\
    %endif                  
  %endfor
  </ul>
</%def>


<%def name="menu(menu_list, active, css_id)">
     <div id="${css_id}" class="yuimenu">
	<div class="bd">
	<ul class ="first-of-type">
	% for i, tuple in enumerate(menu_list):
	  % if i == 0:
	     % if tuple[0] == active:
	       <li class="yuimenuitem first-of-type"><a class="yuimenuitemlabel" href="#${tuple[0]}">${tuple[0]}</a>\
	     % else:	
	       <li class="yuimenuitem first-of-type"><a class="yuimenuitemlabel" href="${tuple[1]}">${tuple[0]}</a>\
	     %endif
	   %else:
	     % if tuple[0] == active:
	       <li class="yuimenuitem"><a class="yuimenuitemlabel" href="#${tuple[0]}">${tuple[0]}</a>\
	     % else:	
	       <li class="yuimenuitem"><a class="yuimenuitemlabel" href="${tuple[1]}">${tuple[0]}</a>\
	     %endif
	   %endif
	  
	  % if len(tuple) > 2: # sub-menus:
	  	${self.menu(tuple[2],active,tuple[0])}
	  %endif    
	%endfor
      </ul>
   </div>
   </div>
</%def>

