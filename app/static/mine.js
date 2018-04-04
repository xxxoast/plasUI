
var accept_task = $('#accept_task_btn');
var deny_task = $('#deny_task_btn');
var city_select = $('#city_select');
var authorize_table = $(#authorize_table);

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
	var city = city_select.val();
    var opt = {
        url: $SCRIPT_ROOT + '/query_all_data/' + toString(city),
        silent: true,
	}
    authorize_table.bootstrapTable('refresh', opt);
});

accept_task.click(function () {
    var indexs = $.map(authorize_table.bootstrapTable('getSelections'), function (json_data) {
        return json_data.index;
    });
    console.log('accept tasks' + indexs);
    submit_table(indexs,$SCRIPT_ROOT + '/auth/accept_task');
    var city = city_select.val();
    var opt = {
        url: $SCRIPT_ROOT + '/query_all_data/' + toString(city),
        silent: true,
	}
	if(city == null || city == "")
		authorize_table.bootstrapTable('refresh');
	else
    	authorize_table.bootstrapTable('refresh',opt);
});

deny_task.click(function () {
    var indexs = $.map(authorize_table.bootstrapTable('getSelections'), function (json_data) {
        return json_data.index;
    });
    console.log('deny tasks ' + indexs);
    //authorize_table.bootstrapTable('remove', {
    //    field: 'index',
    //    values: indexs
    //});
    submit_table(indexs,$SCRIPT_ROOT + '/auth/deny_task');
    var city = city_select.val();
    var opt = {
        url: $SCRIPT_ROOT + '/query_all_data/' + toString(city),
        silent: true,
	}
	if(city == null || city == "")
		authorize_table.bootstrapTable('refresh');
	else
    	authorize_table.bootstrapTable('refresh',opt);
});  