<template>
    <div class="scrHomeBox">
        <div class="header">
           MECNN
        </div>
        <div class="scrHome" style="height:100%;">
            <Row :gutter="16">
                <Col span="6">
                    <div class="colDiv">
                        <div class="chartBox chartLeft" style="height:49.7%">
                            <div class='chartTitle'>
                                <Button icon="ios-cloud-upload-outline" ghost @click="uploadModal=true">Upload Event</Button>
                                &nbsp;
                                <Button ghost @click="handleData">Estimated Magnitude</Button>
                                &nbsp;
                                <Select v-model="dlen">
                                    <Option v-for="item in dlenList" :value="item.value" :key="item.value">{{ item.label }}</Option>
                                </Select>
                                <Modal
                                    footer-hide
                                    v-model="uploadModal"
                                    title="Upload Event">
                                    <div class="form-group">
                                        <label for="folder">Folder Name(Optional)</label>
                                        <input type="text" id="folder" placeholder="file Name（eg：images）" />
                                    </div>
                                    <div class="form-group">
                                        <label for="files">Select Files</label>
                                        <input type="file" id="files" multiple />
                                    </div>
                                    <button @click="uploadFiles">Upload Event</button>
                                </Modal>
                            </div>
                            <div class="ssyjBox" style="height: calc(100% - 50px);margin-top: 10px;">
                                <vxe-table
                                show-overflow
                                ref="xshowTree"
                                height="100%"
                                :data="uploadData"
                                :checkbox-config="{trigger: 'row',  range: true, }"
                                @checkbox-change="checCheckboxkMethod2"
                                :row-config="{isCurrent: true}"
                                :scroll-y="{enabled: true}"
                                :sort-config="{trigger: 'cell'}"
                                row-id="id">
                                <vxe-column type="checkbox" width="45" align="center">
                                </vxe-column>
                                <vxe-column v-for="(item,i) in coulmns1" :key="i+'tree'" :field="item.key" :width="item.width"
                                    :title="item.label">
                                </vxe-column>
                            </vxe-table>
                            </div>
                        </div>
                        <div class="chartBox chartLeft" style="margin: 16px 0;height:49.7%">
                            <div class='chartTitle'>
                            <h4>Historical Earthquake Warning</h4>
                            </div>
                            <div class="ssyjBox">
                                <recycleScrollerLayer ref='recdata1'
                                style="height: 100%;"
                                :limitNum="7"
                                :value="historyData" :coulmn="coulmns"
                                ></recycleScrollerLayer>
                            </div>
                        </div>
                    </div>
                </Col>
                <Col span="18">
                    <div class="colDiv" style="position: relative;">
                        <Row style="position: absolute;top: 0;left: 0;z-index: 999;" class="baseBox">
                            <Col span="6">Lon：{{curYJData.longitude}}</Col>
                            <Col span="6">Lat：{{curYJData.latitude}}</Col>
                            <Col span="6">Mag：{{curYJData.magtrue}}</Col>
                            <Col span="6">Depth：{{curYJData.depth}} km</Col>
                        </Row>
                        <div class="chartBox chartCenter" style="height:100%;padding:0;position: relative;z-index: 100;">
                            <!-- 地图 -->
                            <imgMap ref="imgMapBox" :selcjyData="selcjyData" :language="language" :mapstyle="mapstyle" @getHistoryYJ="getHistoryYJ"></imgMap>
                        </div>
                    </div>
                </Col>
            </Row>
        </div>
    </div>
</template>
<style lang="less">
@import "./syspage.less";
</style>
<script>
import { liquid } from '@/components/charts'
import CountTo from '_c/count-to'
import imgMap from '@/components/mecnn/imgMap.vue'
import recycleScrollerLayer from '@/components/recycle-scroller-layer/recycle-scroller-layer.vue'
import {
  eqcnn,show,hist_magpre
} from '@/api/mecnn.js'
  export default {
    name: 'mecnn',
    components: {
        imgMap,recycleScrollerLayer,liquid,CountTo
    },
    props: [],
    data () {
      return {
        projectName:'',
        scrVisible:false,
        language: 'en',
        mapstyle: 'mapbox://styles/mapbox/satellite-streets-v11',
        curYJData:{
            longitude:'',
            latitude:'',
            magtrue:'',
            depth:''
        },
        curYJList:[],
        selcjyData: {
            longitude: 113.50678976547452,
            latitude: 24.786164345698726
        },
        cityZoom: 1,
        pointCenter: [113.594555, 24.798486],
        dombar: null,
        historyData: [],
        coulmns: [
            {
                width: '25%',
                label: 'Long',
                key: 'longitude'
            },
            {
                width: '25%',
                label: 'Lat',
                key: 'latitude'
            }, {
                width: '25%',
                label: 'Depth',
                key: 'depth'
            }, {
                width: '25%',
                label: 'Mag',
                key: 'magtrue'
            }
        ],
        uploadModal:false,
        uploadData:[],// 上传的文件
        coulmns1: [
            {
                label: 'Id',
                width:"60px",
                key: 'id'
            },
            {
                label: 'File Name',
                key: 'file_name'
            },{
                width:"105px",
                label: 'Folder Name',
                key: 'folder_name'
            }
        ],
        dlen:'300',
        dlenList:[
            { value: '300',label: '3s' },
            { value: '400',label: '4s' },
            { value: '500',label: '5s' },
            { value: '600',label: '6s' },
            { value: '700',label: '7s' },
            { value: '800',label: '8s' },
            { value: '900',label: '9s' },
            { value: '1000',label: '10s' },
        ],
        timer:null,
      }
    },
    watch: {

    },
    created () {
    },
    mounted () {
        this.getHistoryYJ()
        this.handleSuccess()
    },
    methods: {
         // 历史预警
        getHistoryYJ () {
            let that = this
            hist_magpre().then(res => {
                let data = res.data.data
                if(data.length>0){
                    let list = data.map(item => {
                        let obj = {
                            id:item[0],
                            magtrue:(Number(item[1]).toFixed(2))*1,
                            latitude:(Number(item[2]).toFixed(4))*1,
                            longitude:(Number(item[3]).toFixed(4))*1,
                            depth:(Number(item[4]).toFixed(4))*1,
                            wave_len:item[5],
                            file_path:item[6],
                        }
                        return obj
                    })
                    that.curYJData=list[0]
                    setTimeout(() => {
                        that.$refs.imgMapBox.initPopup(list[0])
                    }, 1000)
                    setTimeout(() => {
                        that.getHistoryYJ()
                    }, 1000*60)
                    that.historyData = list
                }
                
            }).catch(err => {
                // //console.log(err);  // that.$Message.error('系统错误')
            })
        },
        // 文件上传
        // 上传文件函数
        async uploadFiles() {
            let that = this
            const fileInput = document.getElementById('files');
            const folderInput = document.getElementById('folder');

            const files = fileInput.files;
            const folder = folderInput.value || "default";  // 如果文件夹为空，使用默认文件夹
            
            if (files.length === 0) {
                that.$Message.error('select file!')
                return;
            }

            // 创建 FormData 对象用于上传
            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
                formData.append("files", files[i]);
            }
            formData.append("folder", folder);

            // 调用 Flask 后端接口上传文件
            try {
                const response = await fetch("http://127.0.0.1:5000/mecnn/upload", {
                    method: "POST",
                    body: formData,
                });

                const data = await response.json();

                if (response.ok) {
                    // 确保 file_paths 是一个数组
                    if (Array.isArray(data.file_paths)) {
                        this.$Message.success('success!');
                    }
                    that.uploadModal=false
                    that.handleSuccess()
                } else {
                    that.$Message.error(`error: ${data.error}`)
                }
            } catch (error) {
                that.$Message.error('error!')
            }
        },
        // 上传成功获取
        handleSuccess () {
            let that = this 
            show().then(res => {
                let data = res.data.files
                let list = data.map(item => {
                    let obj = {
                        id:item[0],
                        folder_name:item[1],
                        file_name:item[2],
                        file_path:item[3]
                    }
                    return obj
                })
                that.uploadData=list
            }).catch((e) => {
                // //console.log(err);  // that.$Message.error('系统错误')
            })
        },
        // 操作复选框时关闭定时器，并且取消高亮
        checCheckboxkMethod2(){
            let that = this
            if(that.timer!=null){
                window.clearTimeout(that.timer)
            }
            that.$refs.xshowTree.clearCurrentRow()
        },
        // 数据处理 eqcnn
        handleData () {
            let that = this 
            if(that.timer!=null){
                window.clearTimeout(that.timer)
            }
            that.curYJList=[]
            let selectRecords = that.$refs.xshowTree.getCheckboxRecords()
            let file_path = []
            if(selectRecords.length>0){
                file_path = (Array.from(selectRecords, ({ file_path }) => file_path))
            }else{
                file_path = (Array.from(that.uploadData, ({ file_path }) => file_path))
            }
            eqcnn({file_path,dlen:that.dlen}).then(res => {
                that.$Message.success('success!');
                let data = res.data
                let num = 0,list=[];
                for(let i in data.depth){
                    let obj = {
                        id:num,
                        magtrue:(Number(data.magpre[i]).toFixed(2)*1),
                        latitude:(Number(data.lat[i]).toFixed(4)*1),
                        longitude:(Number(data.long[i]).toFixed(4)*1),
                        depth:(Number(data.depth[i]).toFixed(4)*1),
                        wave_len:data.wave_len[i],
                        file_path:data.file_path[i],
                    }
                    list.push(obj)
                    num++
                }
                that.curYJData=list[0]
                let index = that.uploadData.map((item) => item.file_path).indexOf(that.curYJData.file_path);
                that.$refs.xshowTree.setCurrentRow(that.uploadData[index])
                setTimeout(() => {
                    that.$refs.imgMapBox.initPopup(list[0])
                }, 1000)
                that.curYJList = list
                that.setTimeFun()
            }).catch((e) => {
                // //console.log(err);  // that.$Message.error('系统错误')
            })
        },
        // 定时更新预警信息
        setTimeFun(){
            let that = this
            if(that.curYJList.length==0){
                return
            }
            that.timer=setTimeout(()=>{
                setTimeout(()=>{
                    let n = Number(that.curYJData.id)+1
                    if(n>=that.curYJList.length){
                        n=0
                    }
                    that.curYJData=that.curYJList[n]
                    let index = that.uploadData.map((item) => item.file_path).indexOf(that.curYJData.file_path);
                    that.$refs.xshowTree.setCurrentRow(that.uploadData[index])
                    setTimeout(() => {
                    that.$refs.imgMapBox.initPopup(that.curYJData)
                }, 1000)
                    that.setTimeFun()
                },1000)
            },5000)
        }
    }
  }
  </script>

  <style lang="less">
    .ssyjBox{
        .vxe-table--render-default .vxe-table--border-line{
            border: none;
        }
        .vxe-table--render-default.border--default .vxe-table--header-wrapper, 
        .vxe-table--render-default.border--full .vxe-table--header-wrapper, 
        .vxe-table--render-default.border--outer .vxe-table--header-wrapper,
        .vxe-table--render-default.border--default .vxe-body--column, 
        .vxe-table--render-default.border--default .vxe-footer--column, 
        .vxe-table--render-default.border--default .vxe-header--column, 
        .vxe-table--render-default.border--inner .vxe-body--column, 
        .vxe-table--render-default.border--inner .vxe-footer--column, 
        .vxe-table--render-default.border--inner .vxe-header--column,
        .vxe-table--render-default .vxe-table--body-wrapper table, 
        .vxe-table--render-default .vxe-table--footer-wrapper table{
            background-color: transparent !important;
            color:#00e9ea;
            background-image:none !important;
        }
        .vxe-header--column .vxe-resizable{
            display: none;
        }
        .is--disabled.vxe-checkbox .vxe-checkbox--icon, 
        .is--disabled.vxe-custom--checkbox-option .vxe-checkbox--icon, 
        .is--disabled.vxe-export--panel-column-option .vxe-checkbox--icon, 
        .is--disabled.vxe-table--filter-option .vxe-checkbox--icon, 
        .vxe-table--render-default .is--disabled.vxe-cell--checkbox .vxe-checkbox--icon,
        .vxe-checkbox .vxe-checkbox--icon, .vxe-custom--checkbox-option .vxe-checkbox--icon, 
        .vxe-export--panel-column-option .vxe-checkbox--icon, 
        .vxe-table--filter-option .vxe-checkbox--icon, 
        .vxe-table--render-default .vxe-cell--checkbox .vxe-checkbox--icon {
            color: #00e9ea !important;
        }
        .vxe-table .vxe-table--header-wrapper .vxe-table--header-border-line{
            border-bottom: 1px solid #00e9ea;
        }
    }
    .form-group {
            margin-bottom: 15px;
        }

        label {
            font-weight: bold;
        }

        input[type="file"] {
            display: block;
            width: 100%;
            padding: 8px;
            margin-top: 8px;
        }

        button {
            display: block;
            width: 100%;
            padding: 10px;
            background-color: #4CAF50;
            color: white;
            border: none;
            font-size: 16px;
            cursor: pointer;
            border-radius: 4px;
        }

        button:hover {
            background-color: #45a049;
        }

        .message {
            text-align: center;
            margin-top: 15px;
        }
  </style>



