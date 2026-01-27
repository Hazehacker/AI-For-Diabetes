<script>
export default {
  onLaunch: function () {
    console.log('App Launch')
  },
  onShow: function () {
    console.log('App Show')
  },
  onHide: function () {
    console.log('App Hide')
  },
}
</script>

<style>
/* 每个页面公共背景，尽量对齐 H5 的 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 */
page {
  min-height: 100vh;
  background: linear-gradient(135deg, #eff6ff 0%, #eef2ff 50%, #faf5ff 100%);
}
</style>
