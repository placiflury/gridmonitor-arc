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
    
    <% MAX_DISPLAY_LEN = 20 %>
	% for i, tuple in enumerate(menu_list):
     
         % if len(tuple[0]) <= MAX_DISPLAY_LEN:
            <%display_name = tuple[0] %>
          %else:
            <%display_name = tuple[0][:MAX_DISPLAY_LEN-3] + '...' %>
         %endif
	 
      % if i == 0:
	     % if tuple[0] == active:
	       <li class="yuimenuitem">
                <a class="yuimenuitemlabel" href="#${tuple[0]}">${display_name}</a>\
	     % else:	
	       <li class="yuimenuitem">
            <a class="yuimenuitemlabel" href="${tuple[1]}">${display_name}</a>\
	     %endif
	   %else:
	     % if tuple[0] == active:
	       <li class="yuimenuitem">
            <a class="yuimenuitemlabel" href="#${tuple[0]}">${display_name}</a>\
	     % else:	
	        <li class="yuimenuitem">
            <a class="yuimenuitemlabel" href="${tuple[1]}">${display_name}</a>\
	     %endif
	   %endif
	  
	  % if len(tuple) > 2: # sub-menus:
        <% unique_id = css_id + h.str_cannonize(tuple[0])%>
	  	${self.menu(tuple[2],active,unique_id)}
	  %endif    
	%endfor
      </ul>
   </div>
   </div>
</%def>

