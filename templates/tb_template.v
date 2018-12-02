//synopsys translate_off
`timescale `DNX_PROJ_TIMESCALE
//synopsys translate_on

module {{TB.tb_name}} ();

// Parameters
{% for parameter in TB.parameters -%}
    localparam {{parameter.name}} = {{parameter.default_value}};
{% endfor %}
// For inputs
{%- for input in TB.inputs -%}
{%- if input.width == "1" %}
reg {{input.name}};
{%- else %}
reg [{{input.width}} - 1 : 0] {{input.name}};
{%- endif -%}
{% endfor %}
// For outputs
{%- for output in TB.outputs -%}
{%- if output.width == "1" %}
wire {{output.name}};
{%- else %}
wire [{{output.width}} - 1 : 0] {{output.name}};
{%- endif -%}
{% endfor %}


// Module instance
{{TB.inst_name}}
{% if TB.parameters -%}
    // Parameters
    #(
    {%- for parameter in TB.parameters[:-1] -%}
        .{{parameter.name}}({{parameter.name}}),
    {% endfor -%}
    .{{TB.parameters[-1].name}}({{TB.parameters[-1].name}}))
{% endif -%}
i_{{TB.inst_name}} (
    // Inputs
    {% for input in TB.inputs -%}
        .{{input.name}}({{input.name}}),
    {% endfor %}
    // Outputs
    {% for output in TB.outputs[:-1] -%}
        .{{output.name}}({{output.name}}),
    {% endfor -%}
    .{{TB.outputs[-1].name}}({{TB.outputs[-1].name}}));

initial begin
    $vcdpluson();
    $vcdplusmemon();
    {% for input in TB.inputs -%}
    {%- if input.name != TB.rst_input.name -%}
        {{input.name}} = {{input.width_numeric}}'d0;
    {%- endif %}
    {% endfor -%}
    // Reset
    {%- if TB.found_rst -%}
    {%- if TB.is_rst_negative %}
    {{TB.rst_input.name}} = 1'b1;
    #1000;
    {{TB.rst_input.name}} = 1'b0;
    #1000;
    {{TB.rst_input.name}} = 1'b1;
    {% else %}
    {{TB.rst_input.name}} = 1'b0;
    #1000;
    {{TB.rst_input.name}} = 1'b1;
    #1000;
    {{TB.rst_input.name}} = 1'b0;
    {% endif -%}
    {%- endif %}

    {% for inputs_dict in TB.list_of_input_dicts -%}
        {% for input, value in inputs_dict.items() %}
    {{input.name}} = {{input.width_numeric}}'d{{value}};
        {%- endfor %}
    #10;
    {% endfor %}

    #1000;
    $finish ;
end

{% if TB.found_clk -%}
always #(5) {{TB.clk_input.name}} = ~{{TB.clk_input.name}};
{%- endif %}

endmodule

