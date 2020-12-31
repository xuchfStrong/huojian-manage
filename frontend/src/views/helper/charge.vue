
<template>
  <div class="app-container">
    <el-form :inline="true" size="mini" class="search_form_wrapper_small" label-width="80px"  label-position="right">
      <el-form-item label="" class="btn-form-item" style="margin-right:0px;">
        <el-button type="primary" size="mini" @click="to_search">搜索</el-button>
        <el-button v-if="isCanExport" type="primary" size="mini" @click="export_xls">导出</el-button>
      </el-form-item>
      
      <el-form-item label="游戏:" >
        <el-select size="mini" v-model="my_pagination.game" placeholder="请选择游戏" filterable clearable style="width: 100%;">
          <el-option
            v-for="item in gameList"
            :key="item.game"
            :label="item.game_name_cn"
            :value="item.game">
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="状态:">
        <el-select size="mini" v-model="my_pagination.status" placeholder="请选择状态" filterable clearable style="width: 100%;">
          <el-option label="成功" :value="0"/>
          <el-option label="撤销" :value="1"/>
          <el-option label="失败" :value="2"/>
        </el-select>
      </el-form-item>
      <el-form-item label="续费ID:">
        <el-input clearable v-model="my_pagination.userid" placeholder="输入精确续费ID"/>
      </el-form-item>
      <el-form-item label="服务器ID:">
        <el-input clearable v-model="my_pagination.server_id" placeholder="输入精确服务器ID"/>
      </el-form-item>
      <el-form-item label="用户:" v-if="isGetUser">
        <el-select size="mini" v-model="my_pagination.user" placeholder="请选择用户" filterable clearable style="width: 100%;">
          <el-option
            v-for="item in userList"
            :key="item.id"
            :label="item.username"
            :value="item.id">
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="开始:">
        <el-date-picker
          v-model="my_pagination.start_time"
          type="date"
          value-format="yyyy-MM-dd"
          placeholder="充值开始日期"
          class="time-picker">
        </el-date-picker>
      </el-form-item>
      <el-form-item label="结束:">
        <el-date-picker
          v-model="my_pagination.end_time"
          type="date"
          value-format="yyyy-MM-dd"
          placeholder="充值结束日期"
          class="time-picker">
        </el-date-picker>
      </el-form-item>
      <el-form-item label="充值类型:">
        <el-select size="mini" v-model="my_pagination.chargetype" placeholder="请选择用户" filterable clearable style="width: 100%;">
          <el-option
            v-for="item in chargetypeList"
            :key="item.id"
            :label="item.type_name_cn"
            :value="item.id">
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="关键字">
        <el-input clearable v-model="my_pagination.search" placeholder="模糊搜索关键字"/>
      </el-form-item>
      <div class="tips">提示：可以输入部分服务器ID或者辅助ID到关键字框进行模糊搜索;只能撤回本周的记录。</div>
    </el-form>

    <!-- <br> -->
    <el-table
      :data="page_datas"
      size="mini"
      border
      stripe
      style="width: 100%">
      <el-table-column prop="id" label="ID" width="50"/>
      <el-table-column  label="用户">
        <template slot-scope="scope">
          {{ scope.row.user.username }}
        </template>
      </el-table-column>
      <el-table-column  label="充值类型">
        <template slot-scope="scope">
          <el-button type="text" size="mini" @click="rowClick(scope.row)"> {{ scope.row.chargetype.type_name_cn }}</el-button>
        </template>
      </el-table-column>
      <el-table-column  label="游戏">
        <template slot-scope="scope">
          {{ scope.row.game.game_name_cn }}
        </template>
      </el-table-column>
      <el-table-column prop="server_id" label="服务器ID"/>
      <el-table-column prop="userid" label="续费ID"/>
      <el-table-column prop="charge_value" label="金额" width="50"/>
      <el-table-column prop="days" label="天数" width="50"/>
      <el-table-column prop="status" label="状态" width="60">
        <template slot-scope="scope">
          <el-tag 
            v-if="scope.row.status"
            :type="scope.row.status === 2 ? 'danger' : 'info'"
            disable-transitions>{{ scope.row.status | statusFilter }}</el-tag>
          <el-tag
            v-else
            type="success"
            disable-transitions>{{ scope.row.status | statusFilter }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="charge_time" label="充值时间" width="135"/>
      <el-table-column prop="old_fuzhu_vip" label="原类型" width="60">
        <template slot-scope="scope">
          {{ scope.row.old_fuzhu_vip | typeFilter }}
        </template>
      </el-table-column>
      <el-table-column prop="fuzhu_vip" label="类型" width="60">
        <template slot-scope="scope">
          {{ scope.row.fuzhu_vip | typeFilter }}
        </template>
      </el-table-column>
      <el-table-column prop="old_end_time" label="原到期时间" width="135"/>
      <el-table-column prop="end_time" label="到期时间" width="135"/>
			<el-table-column prop="content" label="备注"/>
				
      <el-table-column fixed="right" label="操作" align="center">
        <template slot-scope="scope" v-if="$store.getters.user_obj.group.group_type === 'SuperAdmin' || $store.getters.auth_json.charge.auth_update">
          <el-button size="mini" @click="patch_data_fuc(scope.row)">撤销</el-button>
        </template>
      </el-table-column>
    </el-table>
    <br>
    <div class="page-wrap">
      <pagination 
        :total="my_pagination.count" 
        :page.sync="my_pagination.page" 
        :page_size.sync="my_pagination.page_size" 
        @pagination="pag_change"/>
    </div>

    <el-dialog
      :visible.sync="centerDialog_patch"
      v-dialogDrag
      title="确认撤销"
      width="350px"
      center>
      <span>是否确认撤销，撤销后辅助时间和VIP状态将恢复到充值前的状态？</span>
      <span slot="footer" class="dialog-footer">
        <el-button size="mini" @click="centerDialog_patch = false">取 消</el-button>
        <el-button size="mini" type="primary" @click="true_patch">确 定</el-button>
      </span>
    </el-dialog>

    <el-dialog
      :visible.sync="centerDialog_view"
      title="充值详情"
      width="350px"
      center>
      <div class="content-wrap">
        <p v-for="(item, index) in currentResult" :key="index">{{item}}</p>
      </div>
      <div>
        <div>
          <span>状态:</span>
          <span>{{ currentRow.status | statusFilter }}</span>
        </div>
        <div v-if="currentRow.status == 1 && currentRow.reset_user">
          <span>撤销用户:</span>
          <span>{{ currentRow.reset_user.username }}</span>
        </div>
      </div>
    </el-dialog>

  </div>
</template>

<script>
import store from '@/store'
import { exportXls } from '@/api/export'
import { GetAjax, PostAjax, PatchAjax, DeleteAjax } from '@/api/myapi'
import Mysearch from '@/components/SearchField/index2.vue'
import Pagination from '@/components/Pagination'

export default {
  name: 'charge',
  components: { Mysearch, Pagination },
  filters: {
    typeFilter(type) {
      const typeMap = {
        0: '普通版',
        1: 'VIP版'
      }
      return typeMap[type]
    },
    statusFilter(status) {
      const statusMap = {
        0: '成功',
        1: '撤销',
        2: '失败'
      }
      return statusMap[status]
    }
  },
  data() {
    return {
      centerDialog: false,
      centerDialog_delete: false,
      centerDialog_patch: false,
      centerDialog_view: false,
      page_datas: [],
      currentRow: {},
      currentResult: [],
      ruleForm: {},
      rules: {},
      ruleForm_patch: {},
      rules_patch: {},
      currentRow: {},
      gameList: [],
      userList: [],
      chargetypeList: [],
      my_pagination: {
        page: 1,
        page_size: 10,
        count: 0,
        search: '',
        search_type: '',
        start_time: '',
        end_time: ''
      }
    }
  },

  computed: {
    isGetUser() {
      return ['SuperAdmin', 'Admin'].includes(this.$store.getters.user_obj.group.group_type) || this.$store.getters.auth_json.user.auth_list
    },
    isCanExport() {
      return ['SuperAdmin'].includes(this.$store.getters.user_obj.group.group_type)
    }
  },

  created: function() {
    this.get_need_data(this.my_pagination)
    this.get_authGame_data()
    this.get_user_data()
    this.get_chargetype_data()
  },

  methods: {
    tagType(status) {
      const statusMap = {
        0: 'success',
        1: 'info',
        2: 'danger'
      }
      return statusMap[status]
    },

    get_authGame_data(params) {
      GetAjax('/authGame/', params).then(response => {
        this.gameList = this.distinctGame(response.data)
      })
    },

    // 游戏ID去重
    distinctGame(gameData) {
      const result = []
      const gameIds = []
      gameData.forEach(element => {
        if (!gameIds.includes(element.game)) {
          gameIds.push(element.game)
          result.push(element)
        }
      })
      return result
    },

    get_user_data(params) {
      if (this.isGetUser) {
        GetAjax('/userofauth/', params).then(response => {
          this.userList = response.data
        })
      }
    },

    get_chargetype_data(params) {
      GetAjax('/chargetype/', params).then(response => {
        this.chargetypeList = response.data
      })
    },

    get_need_data(params) {
      GetAjax('/charge/', params).then(response => {
        const data = response.data
        this.page_datas = data
        this.my_pagination.count = response.count
      })
    },

    patch_need_data(data) {
      this.centerDialog_patch = false
      PatchAjax('/charge/' + data.id + '/', {}).then(response => {
        const resData = response.data
        this.$message({
          showClose: true,
          message: '撤销成功！',
          type: 'success'
        })
        // for (let index = 0; index < this.page_datas.length; index++) {
        //   if (this.page_datas[index].id === resData.id) {
        //     this.page_datas[index].status = resData.status
        //     this.page_datas[index].charge_value = resData.charge_value
        //     break
        //   }
        // }
        this.get_need_data(this.my_pagination)
      })
    },

    // 修改按钮
    patch_data_fuc(row) {
      this.currentRow = row
      this.centerDialog_patch = true
    },

    // 编辑按钮
    true_patch() {
      this.patch_need_data(this.currentRow)
    },

    // 点击行
    rowClick(row) {
      if (row.result) {
        this.currentRow = JSON.parse(JSON.stringify(row))
        this.currentResult = JSON.parse(this.currentRow.result.replace(/'/g, '"'))
      } else {
        this.currentResult = ["无内容"]
      }
      this.centerDialog_view = true
    },

    // 搜索层相关
    to_search() {
      this.my_pagination.page = 1
      this.get_need_data(this.my_pagination)
    },

    pag_change() {
      this.get_need_data(this.my_pagination)
    },

    search_change() {
      this.get_need_data(this.my_pagination)
    },

    my_change(val) {
      this.my_pagination.page = 1
      this.my_pagination.search_type = val
      this.get_need_data(this.my_pagination)
    },

    export_xls() {
      const exportParams =  JSON.parse(JSON.stringify(this.my_pagination))
      delete exportParams.page
      delete exportParams.page_size
      delete exportParams.count
      delete exportParams.search
      delete exportParams.search_type
      const export_url = process.env.BASE_API + '/exportCharge/'
      exportXls(exportParams, export_url, 'charge.xlsx')
    }
  }
}
</script>

<style>
.el-table .cell .el-tooltip {
  white-space: pre-line;
}
</style>

<style lang='scss' scoped>
.time-picker {
  width: 150px;
}
.tips {
  margin: 10px 0 0 30px;
  font-size: 12px;
  color: #909399;
}
.content-wrap {
	user-select: text;
	word-break: break-all;
}
.page-wrap {
  overflow: auto;
}
</style>
