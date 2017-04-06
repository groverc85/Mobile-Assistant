$(document).ready(function(){
    $('#form1').bootstrapValidator({
        message: '内容无效',
                  feedbackIcons: {
                  valid: 'glyphicon glyphicon-ok',
                  invalid: 'glyphicon glyphicon-remove',
                  validating: 'glyphicon glyphicon-refresh'
                  },
                  fields: {
                      title: {
                      message: '无效的活动名称',
                      validators: {
                          notEmpty: {
                              message: '不能为空'
                          },
                          stringLength: {
                              min: 2,
                              max: 30,
                              message: '活动名称为2到30字'
                          },
                      }
                    },

                      startCity: {
                      message: '请正确选择出发城市',
                      validators: {
                          notEmpty: {
                              message: '不能为空'
                          },
                          stringLength: {
                              min: 2,
                              max: 6,
                              message: '城市名称2-6字'
                          },
                        }
                      },

                      startAddr: {
                      message: '无效的出发地址',
                      validators: {
                          notEmpty: {
                              message: '不能为空'
                          },
                          stringLength: {
                              min: 1,
                              max: 30,
                              message: '出发地址1至30字'
                          },
                        }
                      },

                      destCity: {
                      message: '请正确选择抵达城市',
                      validators: {
                          notEmpty: {
                              message: '不能为空'
                          },
                          stringLength: {
                              min: 2,
                              max: 6,
                              message: '城市名称2-6字'
                          },
                        }
                      },

                      destAddr: {
                      message: '无效的活动地址',
                      validators: {
                          notEmpty: {
                              message: '不能为空'
                          },
                          stringLength: {
                              min: 1,
                              max: 30,
                              message: '1至30字'
                          },
                        }
                      },

                      startTime: {
                      message: '无效的时间',
                      validators: {
                          notEmpty: {
                              message: '不能为空'
                          },
                          stringLength: {
                              min: 2,
                              max: 30,
                              message: '请正确选择开始时间'
                          },
                        }
                      },

                      endTime: {
                      message: '无效的时间',
                      validators: {
                          notEmpty: {
                              message: '不能为空'
                          },
                          stringLength: {
                              min: 2,
                              max: 30,
                              message: '请正确选择结束时间'
                          },
                         
                      }
                    },
                    note: {
                      message: '无效的时间',
                      validators: {
                          stringLength: {
                              min: 0,
                              max: 50,
                              message: '不能超过50字'
                          },
                         
                      }
                    },
                  email: {
                      validators: {
                          notEmpty: {
                              message: 'The email is required and cannot be empty'
                          },
                          emailAddress: {
                              message: 'The input is not a valid email address'
                          }
                      }
                  }
              }
          });
  

    $('#setoutaddress').bind('input propertychange', function(){
        var str = "//map.baidu.com/su?cid=" + $('#setoutcity').val() + '&wd=' + this.value + '&type=0';

        $.ajax({url:str,async:false,dataType:'JSONP',success: function (data) {
            
            
            var rel ='';
            var tem;
            for (i=0;i<data.s.length&&i<=10;i++){
                tem = '<p><span>' + data.s[i].split('$')[0]  + ' ' + data.s[i].split('$')[1] + ' ' + data.s[i].split('$')[3] + ' </span></p>';
                rel = rel.concat(tem);
            }
            $('#addresslist1').html(rel);
            $('#addresslist1').show();
            
            
            $('#addresslist1 p').on('mousedown',function(){
                $('#setoutaddress').val($(this).children("span").html());
                $('#addresslist1').hide();
            
            });
            $('#setoutaddress').blur(function(){
                $('#addresslist1').hide();
            });
        }});
    });
    $('#actaddress').bind('input propertychange', function(){

        var str = "//map.baidu.com/su?cid=" + $('#arrcity').val() + '&wd=' + this.value + '&type=0';

        $.ajax({url:str,async:false,dataType:'JSONP',success: function (data) {
            
            
            var rel ='';
            var tem;
            for (i=0;i<data.s.length&&i<=10;i++){
                tem = '<p><span>' + data.s[i].split('$')[0] + ' ' + data.s[i].split('$')[1] + ' ' + data.s[i].split('$')[3] + '</span></p>';
                rel = rel.concat(tem);
            }
            $('#addresslist2').html(rel);
            $('#addresslist2').show();
            
            
            $('#addresslist2 p').on('mousedown',function(){
                $('#actaddress').val($(this).children("span").html());
                $('#addresslist2').hide();
            
            });
            $('#actaddress').blur(function(){
                $('#addresslist2').hide();
            });
        }});
    });

    $('#setouttime,#acttime').datetimepicker({
       autoclose: true,
       language: "zh-CN",
       format: "yyyy-mm-dd hh:ii",
       startDate: '0d',
       disableTouchKeyboard: true
    });
        
    //城市选择控件
    $('#setoutcity').focus(function(){
        $('#citylist1').show();
    });
    $('#arrcity').focus(function(){
        $('#citylist2').show();
    });
    
    //点选取消城市列表
    $('#table1 td').on('mousedown',function(){
        $('#setoutcity').val(this.innerHTML);
        $('.citylist').hide();
    });
    $('#table2 td').on('mousedown',function(){
        $('#arrcity').val(this.innerHTML);
        $('.citylist').hide();
    });
    $('#setoutcity,#arrcity').blur(function(){
        $('.citylist').hide();
    });
  });