
<template>
  <div class="app-container charge-helper">

    <div>
      <div class="chargetype-wrap">
        <el-radio-group v-model="ruleForm.chargetype" @change="changeChargetype" size="mini" style="margin-bottom:10px;">
          <el-radio v-for="(item, index) in chargetypeList" :key="index" :label="item.id" border>{{item.type_name_cn}}</el-radio>
        </el-radio-group>
      </div>
      <el-form ref="ruleForm" :model="ruleForm" :rules="rules" size="mini" label-width="80px" style="width:300px;">
        <el-form-item label="续费ID" prop="userid">
          <el-input v-model.trim="ruleForm.userid" clearable/>
        </el-form-item>
        <el-form-item label="服务器ID" prop="server_id">
          <el-input v-model.trim="ruleForm.server_id" clearable/>
        </el-form-item>
        <el-form-item label="游戏名称" prop="game">
          <el-select v-model="ruleForm.game" placeholder="请选择游戏" filterable clearable style="width: 100%;">
          <el-option
            v-for="item in gameList"
            :key="item.game"
            :label="item.game_name_cn"
            :value="item.game">
          </el-option>
        </el-select>
        </el-form-item>
        <el-form-item v-if="customTypeChecked" label="充值天数" prop="days">
          <el-input v-model.number="ruleForm.days" clearable/>
        </el-form-item>
        <el-form-item v-if="customTypeChecked" label="充值金额" prop="charge_value">
          <el-input v-model.number="ruleForm.charge_value" clearable/>
        </el-form-item>
        <el-form-item v-if="customTypeChecked" label="是否VIP" prop="fuzhu_vip">
          <el-radio v-model="ruleForm.fuzhu_vip" :label=0 border size="mini">普通</el-radio>
          <el-radio v-model="ruleForm.fuzhu_vip" :label=1 border size="mini">VIP</el-radio>
          <el-radio v-model="ruleForm.fuzhu_vip" :label=10 border size="mini">原状</el-radio>
          <div class="tips2">
            保持原状就是不改变辅助VIP类型。
          </div>
        </el-form-item>
        <el-form-item v-if="customTypeChecked" label="备注" prop="content">
          <el-input v-model="ruleForm.content" clearable :rows=4 type="textarea" placeholder="自定义的类型必须输入原因"/>
        </el-form-item>
      </el-form>
      <div class="tips">
        如果冲错了，直接撤销后再冲，撤销会恢复到充值前的状态； 赠送类型不会改变用户的VIP类型。
      </div>

      <div style="text-align:center;">
        <el-button type="primary" @click="queryUser()">查询</el-button>
        <el-button type="primary" @click="parseUser()">解析</el-button>
        <el-button type="primary" :loading="chargeLoding" @click="submitForm()">充值</el-button>
      </div>

      <div v-if="showResult" class="result-wrap">
        <div class="text-wrap">
          <p v-for="(item, index) in result" :key="index">{{item}}</p>
        </div>
        <div class="flex-button">
          <el-button @click="clearResult()">清空</el-button>
          <div class="right">
            <el-button type="primary" @click="copyResult()">复制</el-button>  
          </div>
        </div>
      </div>
    </div>

    <el-dialog
      :visible.sync="centerDialog_post"
      v-dialogDrag
      title="确认提交"
      width="350px"
      center>
      <span>确认充值信息是否正确？</span>
      <span slot="footer" class="dialog-footer">
        <el-button size="small" @click="centerDialog_post = false">取 消</el-button>
        <el-button size="small" type="primary" @click="true_post">确 定</el-button>
      </span>
    </el-dialog>

    <el-dialog
      :visible.sync="centerDialog_parse"
      v-dialogDrag
      title="解析辅助ID"
      width="350px"
      center>
      <el-input
        v-model="parseText"
        clearable
        :rows=5
        size="mini"
        type="textarea"
        placeholder="将辅助上复制的内容粘贴到这里进行自动解析辅助ID和服务器ID"/>
      <span slot="footer" class="dialog-footer">
        <el-button size="mini" @click="centerDialog_parse = false">取 消</el-button>
        <el-button size="mini" type="primary" @click="true_parse">确 定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { GetAjax, PostAjax, PatchAjax, DeleteAjax } from '@/api/myapi'
import Pagination from '@/components/Pagination'

const defaultRuleForm = {
  server_id: null,
  userid: null,
  game: null,
  days: null,
  fuzhu_vip: 0,
  charge_value: null,
  chargetype: null,
  content: ''
}

export default {
  name: 'chargeHelper',
  components: { Pagination },
  data() {
    return {
      centerDialog_post: false,
      centerDialog_delete: false,
      centerDialog_patch: false,
      centerDialog_parse: false,
      chargeLoding: false,
      chargetypeList: [],
      gameList: [],
      customTypeChecked: false,
      result: [],
      copyText: '',
      parseText: '',
      showResult: false,
      ruleForm: Object.assign({}, defaultRuleForm),
      rules: {
        server_id: [
          { required: true, message: '请输入服务器ID', trigger: 'blur' }
        ],
        userid: [
          { required: true, message: '请输入续费ID', trigger: 'blur' }
        ],
        game: [
          { required: true, message: '请选择游戏', trigger: 'change' }
        ],
        days: [
          { required: true, message: '请输入充值天数', trigger: 'blur' }
        ],
        fuzhu_vip: [
          { required: true, message: '请输入选择辅助类型', trigger: 'change' }
        ],
        charge_value: [
          { required: true, message: '请输入充值金额', trigger: 'blur' }
        ],
        content: [
          { required: true, message: '请输入自定义原因', trigger: 'blur' }
        ],
      },
      ruleForm_patch: {
        
      },
      rules_patch: {
        
      },
      delete_data: {},
      my_pagination: {
        page: 1,
        page_size: 10,
        count: 0,
        search: '',
        search_type: '',
      }
    }
  },

  created: function() {
    this.get_mygame_data()
    this.get_chargetype_data()
  },

  methods: {
    get_mygame_data(params) {
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

    get_chargetype_data(params) {
      GetAjax('/chargetype/', params).then(response => {
        this.chargetypeList = response.data
        this.ruleForm.chargetype = this.chargetypeList[0].id
      })
    },

    post_need_data(params) {
      this.centerDialog_post = false
      if (!this.customTypeChecked) {
        delete params.days
        delete params.fuzhu_vip
        delete params.charge_value
        delete params.content
      }
      this.chargeLoding = true
      PostAjax('/charge/', params).then(response => {
        this.chargeLoding = false
        const data = response.data
        // this.$refs['ruleForm'].resetFields()
        this.result = JSON.parse(data.result.replace(/'/g, '"'))
        this.formatResult()
        this.showResult = true
        this.$message({
          showClose: true,
          message: "充值成功！",
          type: 'success'
        })
      }).catch(err => {
        console.log('err', err)
        this.chargeLoding = false
      })
    },

    // 格式化用于复制的结果
    formatResult() {
      this.copyText = ''
      if (this.result && this.result.length > 0) {
        this.result.forEach(item => {
          this.copyText += item + '\n'
        })
      }
    },

    changeChargetype(value) {
      const choosedChargeType =  this.chargetypeList.find(item => {
        return item.id == value
      })
      this.customTypeChecked = choosedChargeType.decide_type === 1
    },


    submitForm() {
      this.$refs['ruleForm'].validate((valid) => {
        if (valid) {
          this.centerDialog_post= true
        } else {
          console.log('error submit!!')
          return false
        }
      })
    },

    queryUser() {
      this.$refs['ruleForm'].validate((valid) => {
        if (valid) {
          this.get_query_data(this.ruleForm)
        } else {
          console.log('error submit!!')
          return false
        }
      })
    },

    get_query_data(params) {
      GetAjax('/querGameUser/', params).then(response => {
        this.result = response.data.result
        this.formatResult()
        this.showResult = true
        this.$message({
          showClose: true,
          message: "查询成功！",
          type: 'success'
        })
      })
    },

    // 复制内容
    copyResult() {
      this.$copyText(this.copyText).then(
        res => {
          this.$message({
            showClose: true,
            message: "复制成功",
            type: 'success'
          })
        },
        err => {
          this.$message({
            showClose: true,
            message: "复制失败",
            type: 'error'
          })
        }
			)
    },

    // 清空结果
    clearResult() {
      this.result = []
      this.showResult = false
      this.$refs['ruleForm'].resetFields()
    },

    // 确定提交按钮
    true_post() {
      this.post_need_data(this.ruleForm)
    },

    // 自动解析
    parseUser() {
      this.centerDialog_parse = true
      this.parseText = ''
    },

    true_parse() {
      if (this.parseText) {
        const arrSp = this.parseText.split(',')
        this.ruleForm.server_id = arrSp[0].split(':')[1]
        this.ruleForm.userid = arrSp[1].split(':')[1]
        const game_name = arrSp[2]? arrSp[2].split(':')[1] : ''
        this.findGameByName(game_name)
      }
      this.centerDialog_parse = false
    },

    findGameByName(game_name) {
      const gameFind =  this.gameList.find(item => {
        return item.game_name == game_name
      })
      if (gameFind) {
        this.ruleForm.game = gameFind.game
      } else {
        this.ruleForm.game = null
      }
    }
  }
}
</script>


<style lang="scss">
.el-table .cell .el-tooltip {
  white-space: pre-line;
}
.charge-helper {
  .chargetype-wrap {
    .el-radio--mini.is-bordered {
      margin-top: 10px;
      margin-left: 10px;
    }
  }
  .el-radio__inner {
    display: none;
  }
}
</style>
<style lang="scss" scoped>
.result-wrap {
  margin: 10px 0 10px 0;
  .text-wrap {
    background: #F2F6FC;
    padding: 10px;
    margin-bottom: 10px;
    user-select: text;
	  word-break: break-all;
  }
}
.tips {
  margin:0px 0 10px 10px;
  font-size: 12px;
  color: #909399;
}
.tips2 {
  font-size: 12px;
  color: #909399;
}
.flex-button {
  display: flex;
  .left {
    width: 80px;
  }
  .right {
    flex: 1;
    text-align: center;
  }
}
</style>  
