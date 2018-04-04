
var accept_task = $('#accept_task_btn');
var deny_task = $('#deny_task_btn');
var city_select = $('#city_select');
var query_city_select = $('#query_city_select');
var authorize_table = $('#authorize_table');
var select_query_table = $('#query_result_table');

function get_city(){
	return city_select.selectpicker('val');
}

function submit_table(data,tar_url){
	//var data = to_be_submitted.bootstrapTable('getData');
	var json_data = JSON.stringify( data );
	console.log('submit data');
  	$.ajax({
  		type:"POST",
        url: tar_url,
        data: { data : json_data },
        dataType: "json",
       	async: true,
        success: function (data, status) {
        	//var JsonObjs = $.parseJSON(data); 
            if (status == "success") {
                console.log("Success");
            }
        },
        error: function () {
            console.log("error");
        },
        complete: function () {
        }
	});                        	
};	

city_select.on('changed.bs.select',function(e){
	var city = city_select.selectpicker('val');
    var opt = {
        url: $SCRIPT_ROOT + '/auth/query_all_data/' + city + '/',
        silent: true
	};
    authorize_table.bootstrapTable('refresh', opt);
});

query_city_select.on('changed.bs.select',function(e){
	var city = query_city_select.selectpicker('val');
    window.location.href = $SCRIPT_ROOT + '/auth/query/' + city + '/';
});

accept_task.click(function () {
    var indexs = $.map(authorize_table.bootstrapTable('getSelections'), function (json_data) {
        return json_data.index;
    });
    console.log('accept tasks =' + indexs);
    if(indexs.length == 0)
    {
    	alert("请勾选条目");
    	return 0;
    }
    submit_table(indexs,$SCRIPT_ROOT + '/auth/accept_task');
    var city = city_select.selectpicker('val');
    console.log('city = ' + city);
	if(typeof(city) == "undefined")
		authorize_table.bootstrapTable('refresh');
	else{
		console.log('fuck');
		var opt = {
	        url: $SCRIPT_ROOT + '/auth/query_all_data/' + city + '/',
	        silent: true,
		}
		authorize_table.bootstrapTable('remove', {
	    	    field: 'index',
	    	    values: indexs
	    	});
	    	//authorize_table.bootstrapTable('refresh',opt);
	}
});

deny_task.click(function () {
    var indexs = $.map(authorize_table.bootstrapTable('getSelections'), function (json_data) {
        return json_data.index;
    });
    console.log('deny tasks = ' + indexs);
    if(indexs.length == 0)
    {
    	alert("请勾选条目");
    	return 0;
    }
    submit_table(indexs,$SCRIPT_ROOT + '/auth/deny_task');
    var city = city_select.selectpicker('val');
    console.log('city = ' + city);
	if(typeof(city) == "undefined")
		authorize_table.bootstrapTable('refresh');
	else{
		var opt = {
	        url: $SCRIPT_ROOT + '/auth/query_all_data/' + city + '/',
	        silent: true
		};
		authorize_table.bootstrapTable('remove', {
	    	    field: 'index',
	    	    values: indexs
	    	});
    		//authorize_table.bootstrapTable('refresh',opt);
	}
});  

