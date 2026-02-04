/**
 * 图表绘制工具类
 * 用于绘制血糖趋势曲线图
 */

export class GlucoseChartHelper {
  constructor(canvasId, width, height) {
    this.canvasId = canvasId
    this.width = width
    this.height = height
    this.ctx = null
    this.padding = {
      top: 40,
      right: 20,
      bottom: 40,
      left: 50
    }
  }

  /**
   * 初始化画布
   */
  init() {
    return new Promise((resolve, reject) => {
      const query = uni.createSelectorQuery()
      query.select(`#${this.canvasId}`)
        .fields({ node: true, size: true })
        .exec((res) => {
          if (res[0]) {
            const canvas = res[0].node
            this.ctx = canvas.getContext('2d')
            
            const dpr = uni.getSystemInfoSync().pixelRatio
            canvas.width = this.width * dpr
            canvas.height = this.height * dpr
            this.ctx.scale(dpr, dpr)
            
            resolve()
          } else {
            // H5 环境使用传统方式
            this.ctx = uni.createCanvasContext(this.canvasId)
            resolve()
          }
        })
    })
  }

  /**
   * 绘制图表
   * @param {Array} data - 数据点数组 [{timestamp, value}, ...]
   * @param {Object} options - 配置选项
   */
  draw(data, options = {}) {
    if (!this.ctx || !data || data.length === 0) return

    const {
      targetMin = 3.9,
      targetMax = 10.0,
      warningLow = 4.4,
      warningHigh = 9.0,
      showGrid = true,
      showTargetZone = true
    } = options

    // 清空画布
    this.ctx.clearRect(0, 0, this.width, this.height)

    // 计算绘图区域
    const chartWidth = this.width - this.padding.left - this.padding.right
    const chartHeight = this.height - this.padding.top - this.padding.bottom

    // 计算数据范围
    const values = data.map(d => d.value)
    const minValue = Math.min(...values, targetMin)
    const maxValue = Math.max(...values, targetMax)
    const valueRange = maxValue - minValue

    // 绘制背景目标区域
    if (showTargetZone) {
      this.drawTargetZone(chartWidth, chartHeight, minValue, maxValue, targetMin, targetMax)
    }

    // 绘制网格
    if (showGrid) {
      this.drawGrid(chartWidth, chartHeight)
    }

    // 绘制坐标轴
    this.drawAxes(chartWidth, chartHeight, data, minValue, maxValue)

    // 绘制曲线
    this.drawCurve(data, chartWidth, chartHeight, minValue, valueRange)

    // 绘制数据点
    this.drawDataPoints(data, chartWidth, chartHeight, minValue, valueRange, targetMin, targetMax)

    // 如果是传统 canvas，需要调用 draw
    if (this.ctx.draw) {
      this.ctx.draw()
    }
  }

  /**
   * 绘制目标区域
   */
  drawTargetZone(chartWidth, chartHeight, minValue, maxValue, targetMin, targetMax) {
    const yMin = this.valueToY(targetMin, chartHeight, minValue, maxValue - minValue)
    const yMax = this.valueToY(targetMax, chartHeight, minValue, maxValue - minValue)

    this.ctx.fillStyle = 'rgba(16, 185, 129, 0.1)'
    this.ctx.fillRect(
      this.padding.left,
      this.padding.top + yMax,
      chartWidth,
      yMin - yMax
    )
  }

  /**
   * 绘制网格
   */
  drawGrid(chartWidth, chartHeight) {
    this.ctx.strokeStyle = '#E5E7EB'
    this.ctx.lineWidth = 1

    // 水平网格线
    for (let i = 0; i <= 5; i++) {
      const y = this.padding.top + (chartHeight / 5) * i
      this.ctx.beginPath()
      this.ctx.moveTo(this.padding.left, y)
      this.ctx.lineTo(this.padding.left + chartWidth, y)
      this.ctx.stroke()
    }

    // 垂直网格线
    for (let i = 0; i <= 6; i++) {
      const x = this.padding.left + (chartWidth / 6) * i
      this.ctx.beginPath()
      this.ctx.moveTo(x, this.padding.top)
      this.ctx.lineTo(x, this.padding.top + chartHeight)
      this.ctx.stroke()
    }
  }

  /**
   * 绘制坐标轴
   */
  drawAxes(chartWidth, chartHeight, data, minValue, maxValue) {
    this.ctx.strokeStyle = '#9CA3AF'
    this.ctx.lineWidth = 2

    // Y轴
    this.ctx.beginPath()
    this.ctx.moveTo(this.padding.left, this.padding.top)
    this.ctx.lineTo(this.padding.left, this.padding.top + chartHeight)
    this.ctx.stroke()

    // X轴
    this.ctx.beginPath()
    this.ctx.moveTo(this.padding.left, this.padding.top + chartHeight)
    this.ctx.lineTo(this.padding.left + chartWidth, this.padding.top + chartHeight)
    this.ctx.stroke()

    // Y轴刻度
    this.ctx.fillStyle = '#6B7280'
    this.ctx.font = '12px sans-serif'
    this.ctx.textAlign = 'right'
    this.ctx.textBaseline = 'middle'

    for (let i = 0; i <= 5; i++) {
      const value = minValue + ((maxValue - minValue) / 5) * (5 - i)
      const y = this.padding.top + (chartHeight / 5) * i
      this.ctx.fillText(value.toFixed(1), this.padding.left - 10, y)
    }

    // X轴时间标签
    this.ctx.textAlign = 'center'
    this.ctx.textBaseline = 'top'

    if (data.length > 0) {
      const timePoints = [0, Math.floor(data.length / 2), data.length - 1]
      timePoints.forEach(index => {
        if (data[index]) {
          const x = this.padding.left + (chartWidth / (data.length - 1)) * index
          const time = this.formatTime(data[index].timestamp)
          this.ctx.fillText(time, x, this.padding.top + chartHeight + 10)
        }
      })
    }
  }

  /**
   * 绘制曲线
   */
  drawCurve(data, chartWidth, chartHeight, minValue, valueRange) {
    if (data.length < 2) return

    this.ctx.strokeStyle = '#3B82F6'
    this.ctx.lineWidth = 3
    this.ctx.lineJoin = 'round'
    this.ctx.lineCap = 'round'

    this.ctx.beginPath()

    data.forEach((point, index) => {
      const x = this.padding.left + (chartWidth / (data.length - 1)) * index
      const y = this.valueToY(point.value, chartHeight, minValue, valueRange)

      if (index === 0) {
        this.ctx.moveTo(x, this.padding.top + y)
      } else {
        this.ctx.lineTo(x, this.padding.top + y)
      }
    })

    this.ctx.stroke()
  }

  /**
   * 绘制数据点
   */
  drawDataPoints(data, chartWidth, chartHeight, minValue, valueRange, targetMin, targetMax) {
    data.forEach((point, index) => {
      const x = this.padding.left + (chartWidth / (data.length - 1)) * index
      const y = this.valueToY(point.value, chartHeight, minValue, valueRange)

      // 根据血糖值确定颜色
      let color = '#10B981' // 正常
      if (point.value < targetMin || point.value > targetMax) {
        color = '#EF4444' // 危险
      } else if (point.value < targetMin + 0.5 || point.value > targetMax - 1) {
        color = '#F59E0B' // 警告
      }

      this.ctx.fillStyle = color
      this.ctx.beginPath()
      this.ctx.arc(x, this.padding.top + y, 4, 0, Math.PI * 2)
      this.ctx.fill()

      // 外圈
      this.ctx.strokeStyle = '#FFFFFF'
      this.ctx.lineWidth = 2
      this.ctx.stroke()
    })
  }

  /**
   * 将数值转换为Y坐标
   */
  valueToY(value, chartHeight, minValue, valueRange) {
    return chartHeight - ((value - minValue) / valueRange) * chartHeight
  }

  /**
   * 格式化时间
   */
  formatTime(timestamp) {
    const date = new Date(timestamp)
    const hours = date.getHours().toString().padStart(2, '0')
    const minutes = date.getMinutes().toString().padStart(2, '0')
    return `${hours}:${minutes}`
  }

  /**
   * 获取触摸点对应的数据
   */
  getTouchData(x, data, chartWidth) {
    const relativeX = x - this.padding.left
    const index = Math.round((relativeX / chartWidth) * (data.length - 1))
    return data[Math.max(0, Math.min(index, data.length - 1))]
  }
}

/**
 * 生成模拟数据
 */
export function generateMockData(hours = 6) {
  const data = []
  const now = new Date()
  const interval = (hours * 60) / 50 // 生成50个数据点

  for (let i = 0; i < 50; i++) {
    const timestamp = new Date(now.getTime() - (50 - i) * interval * 60 * 1000)
    const baseValue = 5.5 + Math.sin(i / 10) * 2
    const noise = (Math.random() - 0.5) * 1
    const value = Math.max(3.0, Math.min(12.0, baseValue + noise))

    data.push({
      timestamp,
      value: parseFloat(value.toFixed(1))
    })
  }

  return data
}
