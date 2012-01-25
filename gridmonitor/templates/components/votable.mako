<%def name="vo_table(dn, ca, vo_list, voms_connector, type='SLCS')">
    <% voms_connector.reset_dn_ca(dn, ca)%>

    <table width="860">
    <% entries = False %>
    <tr class="table_head"> <th class="gm"colspan="2"> VO membership associated with your ${type} certificate </th> </tr>

    <tr class="table_head2"> <td  colspan="2">DN: <span class="code">${dn}</span></td> </tr>
    <tr class="table_head2"> <td colspan="2"> CA: <span class="code">${ca}</span></td> </tr>
    % for vo in vo_list:
        <% user_groups = voms_connector.listUserGroups(vo) %>
        
        % if user_groups:    
            <% entries = True %>
            <tr class="vo_emph"> 
                <td colspan="2" align="center"> <span class="emph">VO ${vo}</span> </td>
            </tr> 
            <% span = len(user_groups) %>
            <tr> 
                <td rowspan="${span}"> group(s)</td>
                <td><span class="code">${user_groups[0]}</span></td>
            </tr>
            % for group in user_groups[1:]:
                <tr> <td><span class="code">${group}</span></td></tr>
            %endfor
        %endif
        <% user_roles = voms_connector.listUserRoles(vo) %>
        % if user_roles:
            <% entries = True %>
            <% span = len(user_roles) %>
            <tr> <td rowspan="${span}"> role(s)</td>
                <td><span class="code">${user_roles[0]}</span></td>
            </tr>
            % for role in user_roles[1:]:
                <tr><td><span class="code">${role}</span></td></tr>
            % endfor
        %endif
        <% user_attributes = voms_connector.listUserAttributes(vo) %>
        % if user_attributes:
            <% entries = True %>
            <% span = len(user_attributes) %>
            <tr> 
                <td rowspan="${span}"> attribute(s)</td>
                <td><span class="code">${user_attributes[0]}</span></td>
            </tr>
            % for attribute in user_attributes[1:]:
                <tr><td><span class="code"> ${attribute}</span></td></tr>
            % endfor
        %endif
    %endfor
    % if not entries:
        <tr colspan=2> 
            <td align="center"> <span class="warn">No entries on VOMS for this user identity</span> </td>
        </tr>
    % endif
    </table>
</%def>
