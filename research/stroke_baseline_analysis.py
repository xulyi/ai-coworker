import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
import io

# 用户 pasted 的数据
data_text = """分组\t组别说明\t患者ID\t卒中亚型\t时间点\tFMA_LE\tADL\tBBS\tTUGT\tMAS\tCSS
G1\t双侧真实\tSUB-G1-001\t出血性\tT0\t22\t42\t16\tN/A\t2\t13
G1\t双侧真实\tSUB-G1-001\t出血性\tT1\t22\t72\t32\t>42\t1+\t9
G1\t双侧真实\tSUB-G1-001\t出血性\tT2\t23\t82\t37\t29.8\t1\t8
G1\t双侧真实\tSUB-G1-001\t出血性\tT3\t33\t93\t53\t14.1\t1\t7
G1\t双侧真实\tSUB-G1-002\t出血性\tT0\t21\t40\t22\tN/A\t2\t12
G1\t双侧真实\tSUB-G1-002\t出血性\tT1\t24\t49\t36\tN/A\t1+\t10
G1\t双侧真实\tSUB-G1-002\t出血性\tT2\t30\t69\t41\t31.9\t1\t9
G1\t双侧真实\tSUB-G1-002\t出血性\tT3\t31\t78\t46\t12.6\t1\t7
G1\t双侧真实\tSUB-G1-003\t出血性\tT0\t14\t49\t24\t>45\t2\t12
G1\t双侧真实\tSUB-G1-003\t出血性\tT1\t24\t60\t39\t30.7\t1+\t10
G1\t双侧真实\tSUB-G1-003\t出血性\tT2\t32\t64\t41\t19.9\t1\t10
G1\t双侧真实\tSUB-G1-003\t出血性\tT3\t32\t100\t54\t17.3\t1\t8
G1\t双侧真实\tSUB-G1-004\t出血性\tT0\t15\t47\t15\tN/A\t1+\t13
G1\t双侧真实\tSUB-G1-004\t出血性\tT1\t19\t55\t31\tN/A\t1+\t12
G1\t双侧真实\tSUB-G1-004\t出血性\tT2\t32\t67\t47\t11.9\t1\t8
G1\t双侧真实\tSUB-G1-004\t出血性\tT3\t32\t94\t50\t13.4\t1\t8
G1\t双侧真实\tSUB-G1-005\t出血性\tT0\t16\t57\t23\tN/A\t1+\t12
G1\t双侧真实\tSUB-G1-005\t出血性\tT1\t29\t64\t39\t34.4\t1+\t12
G1\t双侧真实\tSUB-G1-005\t出血性\tT2\t29\t90\t39\t32.3\t1\t9
G1\t双侧真实\tSUB-G1-005\t出血性\tT3\t33\t88\t55\t22.2\t0\t8
G1\t双侧真实\tSUB-G1-006\t出血性\tT0\t22\t68\t20\tN/A\t1+\t12
G1\t双侧真实\tSUB-G1-006\t出血性\tT1\t25\t82\t36\tN/A\t1+\t9
G1\t双侧真实\tSUB-G1-006\t出血性\tT2\t28\t92\t47\t17.2\t1\t9
G1\t双侧真实\tSUB-G1-006\t出血性\tT3\t33\t90\t48\t11.5\t1\t8
G1\t双侧真实\tSUB-G1-007\t出血性\tT0\t13\t37\t18\tN/A\t2\t13
G1\t双侧真实\tSUB-G1-007\t出血性\tT1\t24\t79\t29\t>42\t1+\t11
G1\t双侧真实\tSUB-G1-007\t出血性\tT2\t25\t89\t45\t14.9\t1\t9
G1\t双侧真实\tSUB-G1-007\t出血性\tT3\t30\t98\t49\t16.9\t1\t8
G1\t双侧真实\tSUB-G1-008\t出血性\tT0\t15\t53\t24\tN/A\t1+\t13
G1\t双侧真实\tSUB-G1-008\t出血性\tT1\t21\t65\t40\t40.9\t1+\t9
G1\t双侧真实\tSUB-G1-008\t出血性\tT2\t25\t75\t41\t23.2\t1\t9
G1\t双侧真实\tSUB-G1-008\t出血性\tT3\t27\t73\t49\t14.9\t0\t7
G1\t双侧真实\tSUB-G1-009\t出血性\tT0\t15\t53\t36\tN/A\t1+\t12
G1\t双侧真实\tSUB-G1-009\t出血性\tT1\t26\t77\t50\t27.4\t1+\t10
G1\t双侧真实\tSUB-G1-009\t出血性\tT2\t32\t94\t55\t23.7\t1\t8
G1\t双侧真实\tSUB-G1-009\t出血性\tT3\t33\t92\t55\t25.7\t0\t7
G1\t双侧真实\tSUB-G1-010\t出血性\tT0\t16\t54\t34\tN/A\t1+\t13
G1\t双侧真实\tSUB-G1-010\t出血性\tT1\t24\t66\t38\t37.8\t1+\t10
G1\t双侧真实\tSUB-G1-010\t出血性\tT2\t25\t64\t48\t24.5\t1\t9
G1\t双侧真实\tSUB-G1-010\t出血性\tT3\t28\t79\t54\t25.4\t0\t7
G1\t双侧真实\tSUB-G1-011\t出血性\tT0\t23\t55\t19\t>45\t1+\t13
G1\t双侧真实\tSUB-G1-011\t出血性\tT1\t24\t77\t35\tN/A\t1+\t11
G1\t双侧真实\tSUB-G1-011\t出血性\tT2\t26\t75\t35\t>42\t1\t9
G1\t双侧真实\tSUB-G1-011\t出血性\tT3\t32\t86\t51\t18.6\t1\t8
G1\t双侧真实\tSUB-G1-012\t出血性\tT0\t21\t38\t21\tN/A\t2\t12
G1\t双侧真实\tSUB-G1-012\t出血性\tT1\t23\t53\t31\t>42\t1+\t12
G1\t双侧真实\tSUB-G1-012\t出血性\tT2\t28\t78\t47\t25.3\t1\t10
G1\t双侧真实\tSUB-G1-012\t出血性\tT3\t33\t76\t47\t10.1\t0\t8
G1\t双侧真实\tSUB-G1-013\t出血性\tT0\t19\t53\t18\tN/A\t1+\t13
G1\t双侧真实\tSUB-G1-013\t出血性\tT1\t26\t62\t34\tN/A\t1+\t8
G1\t双侧真实\tSUB-G1-013\t出血性\tT2\t30\t84\t50\t25.4\t1\t8
G1\t双侧真实\tSUB-G1-013\t出血性\tT3\t33\t82\t52\t27.3\t1\t7
G1\t双侧真实\tSUB-G1-014\t出血性\tT0\t18\t47\t26\t>45\t1+\t13
G1\t双侧真实\tSUB-G1-014\t出血性\tT1\t26\t63\t42\t15\t1+\t10
G1\t双侧真实\tSUB-G1-014\t出血性\tT2\t31\t67\t43\t17\t1\t9
G1\t双侧真实\tSUB-G1-014\t出血性\tT3\t31\t76\t53\t15.5\t1\t8
G1\t双侧真实\tSUB-G1-015\t出血性\tT0\t20\t54\t20\tN/A\t2\t12
G1\t双侧真实\tSUB-G1-015\t出血性\tT1\t21\t53\t36\t>42\t1+\t9
G1\t双侧真实\tSUB-G1-015\t出血性\tT2\t27\t65\t48\t23.1\t1\t8
G1\t双侧真实\tSUB-G1-015\t出血性\tT3\t27\t82\t53\t15.4\t1\t6
G1\t双侧真实\tSUB-G1-016\t缺血性\tT0\t20\t49\t37\tN/A\t1+\t13
G1\t双侧真实\tSUB-G1-016\t缺血性\tT1\t22\t67\t46\t29.2\t1+\t12
G1\t双侧真实\tSUB-G1-016\t缺血性\tT2\t27\t72\t48\t20.1\t1\t8
G1\t双侧真实\tSUB-G1-016\t缺血性\tT3\t29\t76\t54\t15.7\t1\t7
G1\t双侧真实\tSUB-G1-017\t缺血性\tT0\t19\t57\t27\tN/A\t2\t12
G1\t双侧真实\tSUB-G1-017\t缺血性\tT1\t25\t74\t39\t47.5\t1+\t9
G1\t双侧真实\tSUB-G1-017\t缺血性\tT2\t29\t75\t44\t25.5\t1\t9
G1\t双侧真实\tSUB-G1-017\t缺血性\tT3\t29\t74\t54\t15.2\t0\t8
G1\t双侧真实\tSUB-G1-018\t缺血性\tT0\t22\t71\t30\t>45\t1+\t13
G1\t双侧真实\tSUB-G1-018\t缺血性\tT1\t22\t81\t46\t28.7\t1+\t10
G1\t双侧真实\tSUB-G1-018\t缺血性\tT2\t23\t79\t51\t14.2\t1\t10
G1\t双侧真实\tSUB-G1-018\t缺血性\tT3\t28\t77\t51\t16.2\t1\t8
G1\t双侧真实\tSUB-G1-019\t缺血性\tT0\t21\t66\t35\t>45\t2\t13
G1\t双侧真实\tSUB-G1-019\t缺血性\tT1\t22\t76\t44\t24.4\t1+\t9
G1\t双侧真实\tSUB-G1-019\t缺血性\tT2\t23\t87\t53\t26.4\t1\t9
G1\t双侧真实\tSUB-G1-019\t缺血性\tT3\t31\t85\t55\t18\t0\t8
G1\t双侧真实\tSUB-G1-020\t缺血性\tT0\t27\t66\t32\t>45\t2\t12
G1\t双侧真实\tSUB-G1-020\t缺血性\tT1\t29\t76\t39\t19.4\t1+\t10
G1\t双侧真实\tSUB-G1-020\t缺血性\tT2\t29\t85\t54\t10.6\t1\t8
G1\t双侧真实\tSUB-G1-020\t缺血性\tT3\t30\t83\t54\t12.6\t1\t7
G1\t双侧真实\tSUB-G1-021\t缺血性\tT0\t20\t62\t22\t>45\t1+\t13
G1\t双侧真实\tSUB-G1-021\t缺血性\tT1\t24\t78\t38\t21.9\t1+\t12
G1\t双侧真实\tSUB-G1-021\t缺血性\tT2\t27\t76\t46\t23.9\t1\t9
G1\t双侧真实\tSUB-G1-021\t缺血性\tT3\t28\t74\t51\t17.9\t0\t8
G1\t双侧真实\tSUB-G1-022\t缺血性\tT0\t15\t38\t28\t>45\t1+\t12
G1\t双侧真实\tSUB-G1-022\t缺血性\tT1\t25\t51\t44\t27.9\t1+\t11
G1\t双侧真实\tSUB-G1-022\t缺血性\tT2\t33\t63\t54\t21\t1\t9
G1\t双侧真实\tSUB-G1-022\t缺血性\tT3\t34\t91\t54\t22.9\t1\t6
G1\t双侧真实\tSUB-G1-023\t缺血性\tT0\t25\t49\t27\tN/A\t1+\t12
G1\t双侧真实\tSUB-G1-023\t缺血性\tT1\t27\t69\t41\t27.2\t1+\t10
G1\t双侧真实\tSUB-G1-023\t缺血性\tT2\t29\t72\t52\t16.4\t1\t10
G1\t双侧真实\tSUB-G1-023\t缺血性\tT3\t29\t80\t53\t18.4\t1\t7
G1\t双侧真实\tSUB-G1-024\t缺血性\tT0\t23\t60\t27\tN/A\t2\t13
G1\t双侧真实\tSUB-G1-024\t缺血性\tT1\t26\t73\t30\t>42\t1+\t10
G1\t双侧真实\tSUB-G1-024\t缺血性\tT2\t32\t71\t46\t30.7\t1\t9
G1\t双侧真实\tSUB-G1-024\t缺血性\tT3\t32\t73\t46\t23.6\t1\t7
G1\t双侧真实\tSUB-G1-025\t缺血性\tT0\t21\t57\t16\t>45\t1+\t12
G1\t双侧真实\tSUB-G1-025\t缺血性\tT1\t21\t63\t32\t>42\t1+\t11
G1\t双侧真实\tSUB-G1-025\t缺血性\tT2\t23\t73\t39\t15.2\t1\t8
G1\t双侧真实\tSUB-G1-025\t缺血性\tT3\t29\t71\t54\t17.2\t0\t7
G1\t双侧真实\tSUB-G1-026\t缺血性\tT0\t22\t54\t24\t>45\t1+\t12
G1\t双侧真实\tSUB-G1-026\t缺血性\tT1\t22\t53\t40\t35.4\t1+\t11
G1\t双侧真实\tSUB-G1-026\t缺血性\tT2\t26\t71\t47\t18\t1\t9
G1\t双侧真实\tSUB-G1-026\t缺血性\tT3\t26\t73\t50\t20\t0\t7
G1\t双侧真实\tSUB-G1-027\t缺血性\tT0\t16\t68\t15\t>45\t1+\t12
G1\t双侧真实\tSUB-G1-027\t缺血性\tT1\t20\t66\t31\t>42\t1+\t10
G1\t双侧真实\tSUB-G1-027\t缺血性\tT2\t29\t76\t47\t29.4\t1\t9
G1\t双侧真实\tSUB-G1-027\t缺血性\tT3\t29\t74\t48\t25\t1\t8
G1\t双侧真实\tSUB-G1-028\t缺血性\tT0\t20\t57\t31\t>45\t1+\t13
G1\t双侧真实\tSUB-G1-028\t缺血性\tT1\t23\t67\t44\t27.6\t1+\t9
G1\t双侧真实\tSUB-G1-028\t缺血性\tT2\t29\t65\t46\t21.1\t1\t9
G1\t双侧真实\tSUB-G1-028\t缺血性\tT3\t30\t78\t46\t21\t1\t8
G1\t双侧真实\tSUB-G1-029\t缺血性\tT0\t13\t50\t22\tN/A\t1+\t13
G1\t双侧真实\tSUB-G1-029\t缺血性\tT1\t26\t63\t38\t29.2\t1+\t12
G1\t双侧真实\tSUB-G1-029\t缺血性\tT2\t26\t79\t51\t31.2\t1\t11
G1\t双侧真实\tSUB-G1-029\t缺血性\tT3\t28\t77\t54\t28.1\t1\t8
G1\t双侧真实\tSUB-G1-030\t缺血性\tT0\t19\t42\t35\tN/A\t2\t13
G1\t双侧真实\tSUB-G1-030\t缺血性\tT1\t22\t61\t48\t26.4\t1+\t10
G1\t双侧真实\tSUB-G1-030\t缺血性\tT2\t30\t61\t51\t28.4\t1\t10
G1\t双侧真实\tSUB-G1-030\t缺血性\tT3\t30\t77\t55\t21.6\t0\t8
G2\t单侧真实+对侧安慰剂\tSUB-G2-001\t出血性\tT0\t16\t50\t22\t>45\t2\t13
G2\t单侧真实+对侧安慰剂\tSUB-G2-001\t出血性\tT1\t17\t48\t31\tN/A\t1+\t13
G2\t单侧真实+对侧安慰剂\tSUB-G2-001\t出血性\tT2\t24\t58\t31\tN/A\t1+\t10
G2\t单侧真实+对侧安慰剂\tSUB-G2-001\t出血性\tT3\t26\t75\t38\t35\t1\t8
G2\t单侧真实+对侧安慰剂\tSUB-G2-002\t出血性\tT0\t15\t55\t21\t>45\t2\t13
G2\t单侧真实+对侧安慰剂\tSUB-G2-002\t出血性\tT1\t19\t54\t37\tN/A\t1+\t10
G2\t单侧真实+对侧安慰剂\tSUB-G2-002\t出血性\tT2\t22\t70\t38\t34.6\t1+\t9
G2\t单侧真实+对侧安慰剂\tSUB-G2-002\t出血性\tT3\t26\t81\t38\t35.2\t1\t9
G2\t单侧真实+对侧安慰剂\tSUB-G2-003\t出血性\tT0\t22\t42\t13\t>45\t2\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-003\t出血性\tT1\t25\t42\t29\t>42\t1+\t11
G2\t单侧真实+对侧安慰剂\tSUB-G2-003\t出血性\tT2\t29\t49\t40\t30\t1+\t9
G2\t单侧真实+对侧安慰剂\tSUB-G2-003\t出血性\tT3\t31\t69\t53\t16.9\t1\t8
G2\t单侧真实+对侧安慰剂\tSUB-G2-004\t出血性\tT0\t18\t56\t22\tN/A\t2\t13
G2\t单侧真实+对侧安慰剂\tSUB-G2-004\t出血性\tT1\t22\t63\t29\tN/A\t1+\t13
G2\t单侧真实+对侧安慰剂\tSUB-G2-004\t出血性\tT2\t23\t61\t38\t32\t1+\t10
G2\t单侧真实+对侧安慰剂\tSUB-G2-004\t出血性\tT3\t27\t68\t41\t29.5\t1\t9
G2\t单侧真实+对侧安慰剂\tSUB-G2-005\t出血性\tT0\t17\t50\t28\tN/A\t1+\t13
G2\t单侧真实+对侧安慰剂\tSUB-G2-005\t出血性\tT1\t23\t64\t30\tN/A\t1+\t13
G2\t单侧真实+对侧安慰剂\tSUB-G2-005\t出血性\tT2\t23\t62\t33\t>42\t1+\t11
G2\t单侧真实+对侧安慰剂\tSUB-G2-005\t出血性\tT3\t24\t72\t41\t14.2\t1\t9
G2\t单侧真实+对侧安慰剂\tSUB-G2-006\t出血性\tT0\t20\t55\t34\tN/A\t1+\t13
G2\t单侧真实+对侧安慰剂\tSUB-G2-006\t出血性\tT1\t21\t70\t40\tN/A\t1+\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-006\t出血性\tT2\t28\t80\t51\t13.4\t1+\t10
G2\t单侧真实+对侧安慰剂\tSUB-G2-006\t出血性\tT3\t34\t85\t54\t15.4\t1\t8
G2\t单侧真实+对侧安慰剂\tSUB-G2-007\t出血性\tT0\t21\t45\t25\t>45\t2\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-007\t出血性\tT1\t23\t55\t29\t>42\t1+\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-007\t出血性\tT2\t23\t85\t36\t>42\t1+\t11
G2\t单侧真实+对侧安慰剂\tSUB-G2-007\t出血性\tT3\t24\t95\t45\t20.7\t1\t9
G2\t单侧真实+对侧安慰剂\tSUB-G2-008\t出血性\tT0\t22\t72\t33\t>45\t1+\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-008\t出血性\tT1\t22\t70\t35\tN/A\t1+\t11
G2\t单侧真实+对侧安慰剂\tSUB-G2-008\t出血性\tT2\t22\t75\t44\t40.4\t1+\t11
G2\t单侧真实+对侧安慰剂\tSUB-G2-008\t出血性\tT3\t22\t73\t46\t29.6\t1\t10
G2\t单侧真实+对侧安慰剂\tSUB-G2-009\t出血性\tT0\t18\t33\t25\tN/A\t1+\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-009\t出血性\tT1\t20\t41\t30\tN/A\t1+\t11
G2\t单侧真实+对侧安慰剂\tSUB-G2-009\t出血性\tT2\t24\t63\t46\t32.1\t1+\t8
G2\t单侧真实+对侧安慰剂\tSUB-G2-009\t出血性\tT3\t25\t68\t47\t29.9\t1\t7
G2\t单侧真实+对侧安慰剂\tSUB-G2-010\t出血性\tT0\t22\t57\t24\t>45\t1+\t13
G2\t单侧真实+对侧安慰剂\tSUB-G2-010\t出血性\tT1\t22\t56\t30\tN/A\t1+\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-010\t出血性\tT2\t28\t54\t36\tN/A\t1+\t11
G2\t单侧真实+对侧安慰剂\tSUB-G2-010\t出血性\tT3\t29\t64\t50\t12.1\t1\t9
G2\t单侧真实+对侧安慰剂\tSUB-G2-011\t出血性\tT0\t20\t70\t33\tN/A\t1+\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-011\t出血性\tT1\t20\t68\t35\t>42\t1+\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-011\t出血性\tT2\t21\t78\t44\t20\t1+\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-011\t出血性\tT3\t24\t86\t45\t22\t1\t9
G2\t单侧真实+对侧安慰剂\tSUB-G2-012\t出血性\tT0\t16\t56\t16\tN/A\t2\t13
G2\t单侧真实+对侧安慰剂\tSUB-G2-012\t出血性\tT1\t22\t68\t32\tN/A\t1+\t13
G2\t单侧真实+对侧安慰剂\tSUB-G2-012\t出血性\tT2\t26\t66\t40\t32.6\t1+\t9
G2\t单侧真实+对侧安慰剂\tSUB-G2-012\t出血性\tT3\t29\t66\t40\t25.7\t1\t7
G2\t单侧真实+对侧安慰剂\tSUB-G2-013\t出血性\tT0\t22\t53\t34\tN/A\t1+\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-013\t出血性\tT1\t22\t57\t36\tN/A\t1+\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-013\t出血性\tT2\t26\t65\t43\t35\t1+\t11
G2\t单侧真实+对侧安慰剂\tSUB-G2-013\t出血性\tT3\t28\t63\t47\t13\t1\t9
G2\t单侧真实+对侧安慰剂\tSUB-G2-014\t出血性\tT0\t13\t45\t16\tN/A\t1+\t13
G2\t单侧真实+对侧安慰剂\tSUB-G2-014\t出血性\tT1\t20\t57\t32\tN/A\t1+\t13
G2\t单侧真实+对侧安慰剂\tSUB-G2-014\t出血性\tT2\t24\t64\t39\t44.5\t1+\t11
G2\t单侧真实+对侧安慰剂\tSUB-G2-014\t出血性\tT3\t28\t74\t44\t25\t1\t10
G2\t单侧真实+对侧安慰剂\tSUB-G2-015\t出血性\tT0\t19\t48\t28\tN/A\t2\t13
G2\t单侧真实+对侧安慰剂\tSUB-G2-015\t出血性\tT1\t21\t68\t29\t>42\t1+\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-015\t出血性\tT2\t22\t74\t38\t43.7\t1+\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-015\t出血性\tT3\t26\t72\t40\t25.1\t1\t9
G2\t单侧真实+对侧安慰剂\tSUB-G2-016\t缺血性\tT0\t18\t50\t33\tN/A\t1+\t13
G2\t单侧真实+对侧安慰剂\tSUB-G2-016\t缺血性\tT1\t23\t62\t38\tN/A\t1+\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-016\t缺血性\tT2\t26\t60\t38\t44.8\t1+\t10
G2\t单侧真实+对侧安慰剂\tSUB-G2-016\t缺血性\tT3\t26\t75\t53\t38.7\t1\t9
G2\t单侧真实+对侧安慰剂\tSUB-G2-017\t缺血性\tT0\t26\t63\t27\tN/A\t1+\t13
G2\t单侧真实+对侧安慰剂\tSUB-G2-017\t缺血性\tT1\t27\t61\t35\t>42\t1+\t11
G2\t单侧真实+对侧安慰剂\tSUB-G2-017\t缺血性\tT2\t30\t71\t43\t17.1\t1+\t10
G2\t单侧真实+对侧安慰剂\tSUB-G2-017\t缺血性\tT3\t30\t69\t44\t19.1\t1\t10
G2\t单侧真实+对侧安慰剂\tSUB-G2-018\t缺血性\tT0\t22\t70\t33\tN/A\t1+\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-018\t缺血性\tT1\t22\t68\t38\tN/A\t1+\t11
G2\t单侧真实+对侧安慰剂\tSUB-G2-018\t缺血性\tT2\t26\t67\t39\t36.5\t1+\t11
G2\t单侧真实+对侧安慰剂\tSUB-G2-018\t缺血性\tT3\t30\t65\t42\t34.9\t1\t9
G2\t单侧真实+对侧安慰剂\tSUB-G2-019\t缺血性\tT0\t18\t50\t35\tN/A\t1+\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-019\t缺血性\tT1\t21\t48\t37\tN/A\t1+\t10
G2\t单侧真实+对侧安慰剂\tSUB-G2-019\t缺血性\tT2\t23\t72\t48\t37.7\t1+\t10
G2\t单侧真实+对侧安慰剂\tSUB-G2-019\t缺血性\tT3\t26\t70\t49\t19.1\t1\t8
G2\t单侧真实+对侧安慰剂\tSUB-G2-020\t缺血性\tT0\t20\t37\t18\t>45\t1+\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-020\t缺血性\tT1\t22\t52\t34\t>42\t1+\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-020\t缺血性\tT2\t24\t73\t36\t>42\t1+\t11
G2\t单侧真实+对侧安慰剂\tSUB-G2-020\t缺血性\tT3\t24\t76\t42\t31\t1\t9
G2\t单侧真实+对侧安慰剂\tSUB-G2-021\t缺血性\tT0\t20\t37\t24\tN/A\t2\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-021\t缺血性\tT1\t20\t74\t26\t>42\t1+\t10
G2\t单侧真实+对侧安慰剂\tSUB-G2-021\t缺血性\tT2\t22\t86\t35\t>42\t1+\t10
G2\t单侧真实+对侧安慰剂\tSUB-G2-021\t缺血性\tT3\t23\t96\t41\t14.3\t1\t9
G2\t单侧真实+对侧安慰剂\tSUB-G2-022\t缺血性\tT0\t24\t67\t18\tN/A\t1+\t13
G2\t单侧真实+对侧安慰剂\tSUB-G2-022\t缺血性\tT1\t28\t65\t33\tN/A\t1+\t10
G2\t单侧真实+对侧安慰剂\tSUB-G2-022\t缺血性\tT2\t28\t63\t49\t42.5\t1+\t10
G2\t单侧真实+对侧安慰剂\tSUB-G2-022\t缺血性\tT3\t28\t62\t54\t20.5\t1\t8
G2\t单侧真实+对侧安慰剂\tSUB-G2-023\t缺血性\tT0\t16\t42\t22\t>45\t1+\t13
G2\t单侧真实+对侧安慰剂\tSUB-G2-023\t缺血性\tT1\t17\t51\t38\tN/A\t1+\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-023\t缺血性\tT2\t26\t61\t38\t41.2\t1+\t8
G2\t单侧真实+对侧安慰剂\tSUB-G2-023\t缺血性\tT3\t28\t75\t39\t22.4\t1\t8
G2\t单侧真实+对侧安慰剂\tSUB-G2-024\t缺血性\tT0\t26\t57\t28\tN/A\t2\t13
G2\t单侧真实+对侧安慰剂\tSUB-G2-024\t缺血性\tT1\t26\t62\t29\t>42\t1+\t11
G2\t单侧真实+对侧安慰剂\tSUB-G2-024\t缺血性\tT2\t26\t65\t29\tN/A\t1+\t11
G2\t单侧真实+对侧安慰剂\tSUB-G2-024\t缺血性\tT3\t32\t65\t37\t31.6\t1\t11
G2\t单侧真实+对侧安慰剂\tSUB-G2-025\t缺血性\tT0\t19\t54\t28\tN/A\t1+\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-025\t缺血性\tT1\t22\t62\t28\t>42\t1+\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-025\t缺血性\tT2\t23\t60\t39\t39.8\t1+\t8
G2\t单侧真实+对侧安慰剂\tSUB-G2-025\t缺血性\tT3\t25\t58\t42\t27.9\t1\t8
G2\t单侧真实+对侧安慰剂\tSUB-G2-026\t缺血性\tT0\t23\t39\t23\t>45\t1+\t13
G2\t单侧真实+对侧安慰剂\tSUB-G2-026\t缺血性\tT1\t23\t45\t28\tN/A\t1+\t10
G2\t单侧真实+对侧安慰剂\tSUB-G2-026\t缺血性\tT2\t23\t66\t44\t22.9\t1+\t9
G2\t单侧真实+对侧安慰剂\tSUB-G2-026\t缺血性\tT3\t27\t68\t45\t24.9\t1\t8
G2\t单侧真实+对侧安慰剂\tSUB-G2-027\t缺血性\tT0\t22\t49\t14\t>45\t1+\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-027\t缺血性\tT1\t22\t52\t30\tN/A\t1+\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-027\t缺血性\tT2\t22\t65\t31\t>42\t1+\t9
G2\t单侧真实+对侧安慰剂\tSUB-G2-027\t缺血性\tT3\t26\t84\t41\t26.2\t1\t8
G2\t单侧真实+对侧安慰剂\tSUB-G2-028\t缺血性\tT0\t16\t55\t31\t>45\t2\t13
G2\t单侧真实+对侧安慰剂\tSUB-G2-028\t缺血性\tT1\t17\t56\t33\tN/A\t1+\t11
G2\t单侧真实+对侧安慰剂\tSUB-G2-028\t缺血性\tT2\t25\t72\t38\t18.7\t1+\t11
G2\t单侧真实+对侧安慰剂\tSUB-G2-028\t缺血性\tT3\t25\t70\t45\t20.7\t1\t11
G2\t单侧真实+对侧安慰剂\tSUB-G2-029\t缺血性\tT0\t25\t74\t15\t>45\t2\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-029\t缺血性\tT1\t25\t72\t31\tN/A\t1+\t11
G2\t单侧真实+对侧安慰剂\tSUB-G2-029\t缺血性\tT2\t25\t70\t45\t39.3\t1+\t11
G2\t单侧真实+对侧安慰剂\tSUB-G2-029\t缺血性\tT3\t27\t85\t52\t38.7\t1\t11
G2\t单侧真实+对侧安慰剂\tSUB-G2-030\t缺血性\tT0\t18\t58\t33\tN/A\t2\t13
G2\t单侧真实+对侧安慰剂\tSUB-G2-030\t缺血性\tT1\t21\t57\t33\tN/A\t1+\t12
G2\t单侧真实+对侧安慰剂\tSUB-G2-030\t缺血性\tT2\t24\t68\t38\t16.3\t1+\t10
G2\t单侧真实+对侧安慰剂\tSUB-G2-030\t缺血性\tT3\t24\t68\t40\t18.3\t1\t8
G3\t单侧真实\tSUB-G3-001\t出血性\tT0\t18\t34\t14\tN/A\t2\t13
G3\t单侧真实\tSUB-G3-001\t出血性\tT1\t18\t52\t30\tN/A\t1+\t12
G3\t单侧真实\tSUB-G3-001\t出血性\tT2\t20\t51\t41\t52.7\t1+\t12
G3\t单侧真实\tSUB-G3-001\t出血性\tT3\t21\t70\t50\t30.7\t1\t8
G3\t单侧真实\tSUB-G3-002\t出血性\tT0\t23\t44\t27\tN/A\t1+\t13
G3\t单侧真实\tSUB-G3-002\t出血性\tT1\t26\t55\t35\tN/A\t1+\t11
G3\t单侧真实\tSUB-G3-002\t出血性\tT2\t26\t65\t38\t20.1\t1+\t10
G3\t单侧真实\tSUB-G3-002\t出血性\tT3\t28\t63\t45\t18\t1\t9
G3\t单侧真实\tSUB-G3-003\t出血性\tT0\t18\t58\t37\tN/A\t1+\t12
G3\t单侧真实\tSUB-G3-003\t出血性\tT1\t20\t72\t40\tN/A\t1+\t11
G3\t单侧真实\tSUB-G3-003\t出血性\tT2\t24\t82\t40\t24.9\t1+\t11
G3\t单侧真实\tSUB-G3-003\t出血性\tT3\t27\t84\t42\t20.1\t1\t11
G3\t单侧真实\tSUB-G3-004\t出血性\tT0\t15\t67\t16\tN/A\t2\t13
G3\t单侧真实\tSUB-G3-004\t出血性\tT1\t23\t78\t24\t>42\t1+\t12
G3\t单侧真实\tSUB-G3-004\t出血性\tT2\t26\t88\t38\t28.1\t1+\t11
G3\t单侧真实\tSUB-G3-004\t出血性\tT3\t27\t86\t46\t14.8\t1\t8
G3\t单侧真实\tSUB-G3-005\t出血性\tT0\t16\t39\t33\tN/A\t1+\t13
G3\t单侧真实\tSUB-G3-005\t出血性\tT1\t23\t53\t33\t>42\t1+\t12
G3\t单侧真实\tSUB-G3-005\t出血性\tT2\t23\t59\t42\t35.8\t1+\t10
G3\t单侧真实\tSUB-G3-005\t出血性\tT3\t26\t60\t43\t17\t1\t7
G3\t单侧真实\tSUB-G3-006\t出血性\tT0\t14\t55\t31\t>45\t2\t12
G3\t单侧真实\tSUB-G3-006\t出血性\tT1\t16\t53\t35\tN/A\t1+\t11
G3\t单侧真实\tSUB-G3-006\t出血性\tT2\t21\t51\t41\t36.8\t1+\t10
G3\t单侧真实\tSUB-G3-006\t出血性\tT3\t31\t75\t41\t30.9\t1\t10
G3\t单侧真实\tSUB-G3-007\t出血性\tT0\t22\t70\t27\tN/A\t2\t12
G3\t单侧真实\tSUB-G3-007\t出血性\tT1\t22\t68\t33\tN/A\t1+\t12
G3\t单侧真实\tSUB-G3-007\t出血性\tT2\t22\t66\t35\tN/A\t1+\t12
G3\t单侧真实\tSUB-G3-007\t出血性\tT3\t31\t76\t43\t20.3\t1\t8
G3\t单侧真实\tSUB-G3-008\t出血性\tT0\t17\t45\t23\t>45\t1+\t12
G3\t单侧真实\tSUB-G3-008\t出血性\tT1\t19\t43\t30\t>42\t1+\t11
G3\t单侧真实\tSUB-G3-008\t出血性\tT2\t22\t69\t42\t31.8\t1+\t9
G3\t单侧真实\tSUB-G3-008\t出血性\tT3\t25\t70\t43\t23.7\t1\t8
G3\t单侧真实\tSUB-G3-009\t出血性\tT0\t17\t47\t27\t>45\t1+\t12
G3\t单侧真实\tSUB-G3-009\t出血性\tT1\t19\t48\t27\t>42\t1+\t11
G3\t单侧真实\tSUB-G3-009\t出血性\tT2\t19\t69\t36\tN/A\t1+\t10
G3\t单侧真实\tSUB-G3-009\t出血性\tT3\t21\t79\t41\t16.5\t1\t9
G3\t单侧真实\tSUB-G3-010\t出血性\tT0\t16\t39\t20\tN/A\t2\t12
G3\t单侧真实\tSUB-G3-010\t出血性\tT1\t23\t49\t36\t>42\t1+\t12
G3\t单侧真实\tSUB-G3-010\t出血性\tT2\t25\t57\t39\t36.1\t1+\t11
G3\t单侧真实\tSUB-G3-010\t出血性\tT3\t28\t66\t39\t14.1\t1\t10
G3\t单侧真实\tSUB-G3-011\t出血性\tT0\t15\t46\t19\tN/A\t2\t13
G3\t单侧真实\tSUB-G3-011\t出血性\tT1\t22\t53\t24\t>42\t1+\t12
G3\t单侧真实\tSUB-G3-011\t出血性\tT2\t24\t68\t29\tN/A\t1+\t10
G3\t单侧真实\tSUB-G3-011\t出血性\tT3\t27\t88\t42\t20.8\t1\t10
G3\t单侧真实\tSUB-G3-012\t出血性\tT0\t17\t44\t33\t>45\t2\t13
G3\t单侧真实\tSUB-G3-012\t出血性\tT1\t18\t64\t35\t>42\t1+\t11
G3\t单侧真实\tSUB-G3-012\t出血性\tT2\t23\t76\t35\t>42\t1+\t9
G3\t单侧真实\tSUB-G3-012\t出血性\tT3\t26\t74\t37\t38.8\t1\t7
G3\t单侧真实\tSUB-G3-013\t出血性\tT0\t22\t53\t13\tN/A\t2\t13
G3\t单侧真实\tSUB-G3-013\t出血性\tT1\t22\t51\t29\tN/A\t1+\t11
G3\t单侧真实\tSUB-G3-013\t出血性\tT2\t27\t61\t45\t27\t1+\t10
G3\t单侧真实\tSUB-G3-013\t出血性\tT3\t30\t70\t48\t26\t1\t7
G3\t单侧真实\tSUB-G3-014\t出血性\tT0\t18\t40\t24\t>45\t1+\t12
G3\t单侧真实\tSUB-G3-014\t出血性\tT1\t22\t50\t29\t>42\t1+\t11
G3\t单侧真实\tSUB-G3-014\t出血性\tT2\t24\t56\t31\tN/A\t1+\t10
G3\t单侧真实\tSUB-G3-014\t出血性\tT3\t30\t66\t38\t24.7\t1\t10
G3\t单侧真实\tSUB-G3-015\t出血性\tT0\t21\t49\t25\tN/A\t1+\t13
G3\t单侧真实\tSUB-G3-015\t出血性\tT1\t24\t61\t27\t>42\t1+\t12
G3\t单侧真实\tSUB-G3-015\t出血性\tT2\t28\t66\t43\t51.3\t1+\t12
G3\t单侧真实\tSUB-G3-015\t出血性\tT3\t29\t73\t45\t29.4\t1\t10
G3\t单侧真实\tSUB-G3-016\t缺血性\tT0\t22\t62\t28\t>45\t2\t12
G3\t单侧真实\tSUB-G3-016\t缺血性\tT1\t24\t60\t28\t>42\t1+\t11
G3\t单侧真实\tSUB-G3-016\t缺血性\tT2\t26\t58\t32\tN/A\t1+\t10
G3\t单侧真实\tSUB-G3-016\t缺血性\tT3\t28\t78\t44\t30.6\t1\t9
G3\t单侧真实\tSUB-G3-017\t缺血性\tT0\t18\t74\t17\t>45\t1+\t13
G3\t单侧真实\tSUB-G3-017\t缺血性\tT1\t21\t72\t29\tN/A\t1+\t12
G3\t单侧真实\tSUB-G3-017\t缺血性\tT2\t23\t78\t35\t>42\t1+\t10
G3\t单侧真实\tSUB-G3-017\t缺血性\tT3\t24\t76\t49\t30.8\t1\t10
G3\t单侧真实\tSUB-G3-018\t缺血性\tT0\t23\t74\t24\tN/A\t2\t13
G3\t单侧真实\tSUB-G3-018\t缺血性\tT1\t23\t72\t36\tN/A\t1+\t12
G3\t单侧真实\tSUB-G3-018\t缺血性\tT2\t23\t70\t36\tN/A\t1+\t11
G3\t单侧真实\tSUB-G3-018\t缺血性\tT3\t29\t78\t47\t30.7\t1\t11
G3\t单侧真实\tSUB-G3-019\t缺血性\tT0\t18\t46\t22\t>45\t1+\t12
G3\t单侧真实\tSUB-G3-019\t缺血性\tT1\t19\t54\t29\tN/A\t1+\t11
G3\t单侧真实\tSUB-G3-019\t缺血性\tT2\t22\t64\t34\t>42\t1+\t10
G3\t单侧真实\tSUB-G3-019\t缺血性\tT3\t24\t69\t40\t38.7\t1\t9
G3\t单侧真实\tSUB-G3-020\t缺血性\tT0\t24\t50\t18\tN/A\t2\t13
G3\t单侧真实\tSUB-G3-020\t缺血性\tT1\t24\t48\t33\tN/A\t1+\t11
G3\t单侧真实\tSUB-G3-020\t缺血性\tT2\t30\t69\t38\t14.9\t1+\t10
G3\t单侧真实\tSUB-G3-020\t缺血性\tT3\t32\t75\t38\t16.9\t1\t9
G3\t单侧真实\tSUB-G3-021\t缺血性\tT0\t14\t65\t22\tN/A\t1+\t12
G3\t单侧真实\tSUB-G3-021\t缺血性\tT1\t20\t63\t30\t>42\t1+\t11
G3\t单侧真实\tSUB-G3-021\t缺血性\tT2\t21\t72\t43\t35.2\t1+\t10
G3\t单侧真实\tSUB-G3-021\t缺血性\tT3\t24\t80\t44\t31.9\t1\t9
G3\t单侧真实\tSUB-G3-022\t缺血性\tT0\t14\t36\t30\tN/A\t1+\t13
G3\t单侧真实\tSUB-G3-022\t缺血性\tT1\t15\t54\t36\tN/A\t1+\t13
G3\t单侧真实\tSUB-G3-022\t缺血性\tT2\t28\t79\t45\t16.8\t1+\t9
G3\t单侧真实\tSUB-G3-022\t缺血性\tT3\t31\t77\t45\t18.8\t1\t9
G3\t单侧真实\tSUB-G3-023\t缺血性\tT0\t26\t63\t29\tN/A\t1+\t13
G3\t单侧真实\tSUB-G3-023\t缺血性\tT1\t26\t63\t36\tN/A\t1+\t13
G3\t单侧真实\tSUB-G3-023\t缺血性\tT2\t30\t62\t39\t52.5\t1+\t10
G3\t单侧真实\tSUB-G3-023\t缺血性\tT3\t30\t60\t41\t30.5\t1\t8
G3\t单侧真实\tSUB-G3-024\t缺血性\tT0\t22\t67\t37\tN/A\t1+\t13
G3\t单侧真实\tSUB-G3-024\t缺血性\tT1\t22\t65\t37\tN/A\t1+\t12
G3\t单侧真实\tSUB-G3-024\t缺血性\tT2\t22\t75\t49\t29\t1+\t10
G3\t单侧真实\tSUB-G3-024\t缺血性\tT3\t26\t79\t49\t16.1\t1\t10
G3\t单侧真实\tSUB-G3-025\t缺血性\tT0\t24\t52\t28\t>45\t1+\t12
G3\t单侧真实\tSUB-G3-025\t缺血性\tT1\t24\t58\t39\tN/A\t1+\t12
G3\t单侧真实\tSUB-G3-025\t缺血性\tT2\t24\t59\t46\t39.5\t1+\t11
G3\t单侧真实\tSUB-G3-025\t缺血性\tT3\t25\t57\t51\t25.2\t1\t10
G3\t单侧真实\tSUB-G3-026\t缺血性\tT0\t23\t48\t26\t>45\t1+\t12
G3\t单侧真实\tSUB-G3-026\t缺血性\tT1\t23\t56\t31\t>42\t1+\t12
G3\t单侧真实\tSUB-G3-026\t缺血性\tT2\t24\t75\t43\t30.5\t1+\t11
G3\t单侧真实\tSUB-G3-026\t缺血性\tT3\t25\t73\t43\t31.2\t1\t10
G3\t单侧真实\tSUB-G3-027\t缺血性\tT0\t19\t50\t25\tN/A\t1+\t13
G3\t单侧真实\tSUB-G3-027\t缺血性\tT1\t22\t61\t30\t>42\t1+\t11
G3\t单侧真实\tSUB-G3-027\t缺血性\tT2\t25\t59\t37\t33.1\t1+\t11
G3\t单侧真实\tSUB-G3-027\t缺血性\tT3\t27\t66\t45\t24.6\t1\t8
G3\t单侧真实\tSUB-G3-028\t缺血性\tT0\t23\t54\t19\tN/A\t2\t12
G3\t单侧真实\tSUB-G3-028\t缺血性\tT1\t25\t52\t32\tN/A\t1+\t11
G3\t单侧真实\tSUB-G3-028\t缺血性\tT2\t25\t65\t36\tN/A\t1+\t11
G3\t单侧真实\tSUB-G3-028\t缺血性\tT3\t28\t75\t50\t28\t1\t10
G3\t单侧真实\tSUB-G3-029\t缺血性\tT0\t15\t52\t29\tN/A\t1+\t13
G3\t单侧真实\tSUB-G3-029\t缺血性\tT1\t24\t63\t29\t>42\t1+\t13
G3\t单侧真实\tSUB-G3-029\t缺血性\tT2\t24\t61\t35\t>42\t1+\t11
G3\t单侧真实\tSUB-G3-029\t缺血性\tT3\t24\t65\t51\t30.3\t1\t9
G3\t单侧真实\tSUB-G3-030\t缺血性\tT0\t23\t61\t23\tN/A\t2\t13
G3\t单侧真实\tSUB-G3-030\t缺血性\tT1\t23\t64\t31\tN/A\t1+\t13
G3\t单侧真实\tSUB-G3-030\t缺血性\tT2\t25\t62\t45\t45.5\t1+\t11
G3\t单侧真实\tSUB-G3-030\t缺血性\tT3\t29\t69\t45\t23.5\t1\t9
G4\t空白对照(CT)\tSUB-G4-001\t出血性\tT0\t23\t45\t21\tN/A\t2\t12
G4\t空白对照(CT)\tSUB-G4-001\t出血性\tT1\t25\t45\t25\tN/A\t2\t12
G4\t空白对照(CT)\tSUB-G4-001\t出血性\tT2\t26\t50\t41\tN/A\t1+\t11
G4\t空白对照(CT)\tSUB-G4-001\t出血性\tT3\t26\t61\t44\t25.7\t1+\t9
G4\t空白对照(CT)\tSUB-G4-002\t出血性\tT0\t20\t35\t13\tN/A\t1+\t12
G4\t空白对照(CT)\tSUB-G4-002\t出血性\tT1\t23\t42\t26\tN/A\t1+\t12
G4\t空白对照(CT)\tSUB-G4-002\t出血性\tT2\t27\t55\t31\tN/A\t1+\t10
G4\t空白对照(CT)\tSUB-G4-002\t出血性\tT3\t28\t53\t37\t50.6\t1+\t10
G4\t空白对照(CT)\tSUB-G4-003\t出血性\tT0\t15\t44\t32\tN/A\t2\t12
G4\t空白对照(CT)\tSUB-G4-003\t出血性\tT1\t16\t63\t32\tN/A\t1+\t12
G4\t空白对照(CT)\tSUB-G4-003\t出血性\tT2\t19\t61\t32\tN/A\t1+\t12
G4\t空白对照(CT)\tSUB-G4-003\t出血性\tT3\t27\t71\t41\t17.5\t1+\t11
G4\t空白对照(CT)\tSUB-G4-004\t出血性\tT0\t20\t56\t32\tN/A\t1+\t12
G4\t空白对照(CT)\tSUB-G4-004\t出血性\tT1\t20\t62\t33\tN/A\t1+\t12
G4\t空白对照(CT)\tSUB-G4-004\t出血性\tT2\t20\t60\t33\tN/A\t1+\t12
G4\t空白对照(CT)\tSUB-G4-004\t出血性\tT3\t22\t69\t37\t37.2\t1+\t12
G4\t空白对照(CT)\tSUB-G4-005\t出血性\tT0\t19\t50\t18\t>45\t1+\t12
G4\t空白对照(CT)\tSUB-G4-005\t出血性\tT1\t21\t48\t22\tN/A\t2\t12
G4\t空白对照(CT)\tSUB-G4-005\t出血性\tT2\t25\t59\t28\t>42\t1+\t12
G4\t空白对照(CT)\tSUB-G4-005\t出血性\tT3\t25\t69\t38\t19.5\t1+\t10
G4\t空白对照(CT)\tSUB-G4-006\t出血性\tT0\t21\t39\t26\t>45\t1+\t13
G4\t空白对照(CT)\tSUB-G4-006\t出血性\tT1\t21\t56\t26\t>42\t2\t13
G4\t空白对照(CT)\tSUB-G4-006\t出血性\tT2\t21\t70\t40\tN/A\t1+\t13
G4\t空白对照(CT)\tSUB-G4-006\t出血性\tT3\t21\t80\t42\t29.4\t1+\t9
G4\t空白对照(CT)\tSUB-G4-007\t出血性\tT0\t15\t55\t24\t>45\t2\t12
G4\t空白对照(CT)\tSUB-G4-007\t出血性\tT1\t17\t57\t29\tN/A\t2\t12
G4\t空白对照(CT)\tSUB-G4-007\t出血性\tT2\t22\t67\t29\t>42\t1+\t9
G4\t空白对照(CT)\tSUB-G4-007\t出血性\tT3\t23\t65\t37\t37.6\t1+\t9
G4\t空白对照(CT)\tSUB-G4-008\t出血性\tT0\t13\t45\t22\t>45\t2\t13
G4\t空白对照(CT)\tSUB-G4-008\t出血性\tT1\t21\t45\t23\t>42\t1+\t13
G4\t空白对照(CT)\tSUB-G4-008\t出血性\tT2\t23\t58\t31\t>42\t1+\t13
G4\t空白对照(CT)\tSUB-G4-008\t出血性\tT3\t28\t62\t47\t46.9\t1+\t11
G4\t空白对照(CT)\tSUB-G4-009\t出血性\tT0\t20\t57\t32\tN/A\t2\t13
G4\t空白对照(CT)\tSUB-G4-009\t出血性\tT1\t21\t55\t34\tN/A\t2\t12
G4\t空白对照(CT)\tSUB-G4-009\t出血性\tT2\t23\t69\t36\tN/A\t1+\t11
G4\t空白对照(CT)\tSUB-G4-009\t出血性\tT3\t25\t67\t37\t44.2\t1+\t10
G4\t空白对照(CT)\tSUB-G4-010\t出血性\tT0\t15\t49\t20\t>45\t1+\t12
G4\t空白对照(CT)\tSUB-G4-010\t出血性\tT1\t18\t50\t22\t>42\t2\t12
G4\t空白对照(CT)\tSUB-G4-010\t出血性\tT2\t24\t58\t35\tN/A\t1+\t11
G4\t空白对照(CT)\tSUB-G4-010\t出血性\tT3\t25\t68\t38\t24.3\t1+\t11
G4\t空白对照(CT)\tSUB-G4-011\t出血性\tT0\t18\t63\t29\tN/A\t1+\t12
G4\t空白对照(CT)\tSUB-G4-011\t出血性\tT1\t18\t61\t29\t>42\t1+\t11
G4\t空白对照(CT)\tSUB-G4-011\t出血性\tT2\t20\t64\t31\tN/A\t1+\t9
G4\t空白对照(CT)\tSUB-G4-011\t出血性\tT3\t26\t74\t39\t27.5\t1+\t9
G4\t空白对照(CT)\tSUB-G4-012\t出血性\tT0\t19\t48\t15\tN/A\t1+\t13
G4\t空白对照(CT)\tSUB-G4-012\t出血性\tT1\t20\t46\t18\t>42\t2\t11
G4\t空白对照(CT)\tSUB-G4-012\t出血性\tT2\t24\t57\t25\tN/A\t1+\t11
G4\t空白对照(CT)\tSUB-G4-012\t出血性\tT3\t27\t67\t38\t19.9\t1+\t11
G4\t空白对照(CT)\tSUB-G4-013\t出血性\tT0\t23\t59\t28\t>45\t1+\t12
G4\t空白对照(CT)\tSUB-G4-013\t出血性\tT1\t23\t57\t31\tN/A\t1+\t12
G4\t空白对照(CT)\tSUB-G4-013\t出血性\tT2\t25\t55\t32\tN/A\t1+\t10
G4\t空白对照(CT)\tSUB-G4-013\t出血性\tT3\t27\t65\t37\t29.6\t1+\t10
G4\t空白对照(CT)\tSUB-G4-014\t出血性\tT0\t20\t56\t32\tN/A\t1+\t12
G4\t空白对照(CT)\tSUB-G4-014\t出血性\tT1\t20\t62\t33\tN/A\t1+\t12
G4\t空白对照(CT)\tSUB-G4-014\t出血性\tT2\t20\t60\t33\tN/A\t1+\t12
G4\t空白对照(CT)\tSUB-G4-014\t出血性\tT3\t22\t69\t37\t37.2\t1+\t12
G4\t空白对照(CT)\tSUB-G4-015\t出血性\tT0\t18\t47\t23\t>45\t2\t13
G4\t空白对照(CT)\tSUB-G4-015\t出血性\tT1\t20\t48\t28\tN/A\t2\t12
G4\t空白对照(CT)\tSUB-G4-015\t出血性\tT2\t20\t56\t30\tN/A\t1+\t12
G4\t空白对照(CT)\tSUB-G4-015\t出血性\tT3\t22\t66\t37\t27.4\t1+\t10
G4\t空白对照(CT)\tSUB-G4-016\t缺血性\tT0\t17\t42\t18\tN/A\t2\t13
G4\t空白对照(CT)\tSUB-G4-016\t缺血性\tT1\t17\t52\t27\t>42\t2\t12
G4\t空白对照(CT)\tSUB-G4-016\t缺血性\tT2\t26\t63\t28\tN/A\t1+\t11
G4\t空白对照(CT)\tSUB-G4-016\t缺血性\tT3\t29\t61\t37\t32.4\t1+\t11
G4\t空白对照(CT)\tSUB-G4-017\t缺血性\tT0\t22\t61\t30\tN/A\t1+\t13
G4\t空白对照(CT)\tSUB-G4-017\t缺血性\tT1\t24\t59\t30\t>42\t1+\t13
G4\t空白对照(CT)\tSUB-G4-017\t缺血性\tT2\t25\t62\t34\t>42\t1+\t13
G4\t空白对照(CT)\tSUB-G4-017\t缺血性\tT3\t27\t65\t48\t49.5\t1+\t10
G4\t空白对照(CT)\tSUB-G4-018\t缺血性\tT0\t25\t62\t24\tN/A\t2\t12
G4\t空白对照(CT)\tSUB-G4-018\t缺血性\tT1\t25\t62\t26\t>42\t1+\t11
G4\t空白对照(CT)\tSUB-G4-018\t缺血性\tT2\t25\t60\t28\tN/A\t1+\t11
G4\t空白对照(CT)\tSUB-G4-018\t缺血性\tT3\t28\t70\t37\t27.1\t1+\t11
G4\t空白对照(CT)\tSUB-G4-019\t缺血性\tT0\t19\t55\t19\t>45\t2\t12
G4\t空白对照(CT)\tSUB-G4-019\t缺血性\tT1\t19\t53\t29\t>42\t2\t12
G4\t空白对照(CT)\tSUB-G4-019\t缺血性\tT2\t22\t68\t31\tN/A\t1+\t12
G4\t空白对照(CT)\tSUB-G4-019\t缺血性\tT3\t23\t74\t37\t53.6\t1+\t10
G4\t空白对照(CT)\tSUB-G4-020\t缺血性\tT0\t20\t60\t29\t>45\t2\t13
G4\t空白对照(CT)\tSUB-G4-020\t缺血性\tT1\t22\t67\t34\t>42\t2\t12
G4\t空白对照(CT)\tSUB-G4-020\t缺血性\tT2\t23\t65\t34\tN/A\t1+\t12
G4\t空白对照(CT)\tSUB-G4-020\t缺血性\tT3\t23\t63\t37\t30.2\t1+\t12
G4\t空白对照(CT)\tSUB-G4-021\t缺血性\tT0\t15\t55\t30\t>45\t2\t13
G4\t空白对照(CT)\tSUB-G4-021\t缺血性\tT1\t17\t59\t33\tN/A\t2\t13
G4\t空白对照(CT)\tSUB-G4-021\t缺血性\tT2\t23\t69\t34\t>42\t1+\t12
G4\t空白对照(CT)\tSUB-G4-021\t缺血性\tT3\t23\t67\t40\t35.8\t1+\t12
G4\t空白对照(CT)\tSUB-G4-022\t缺血性\tT0\t19\t61\t26\t>45\t2\t13
G4\t空白对照(CT)\tSUB-G4-022\t缺血性\tT1\t19\t62\t36\tN/A\t2\t10
G4\t空白对照(CT)\tSUB-G4-022\t缺血性\tT2\t20\t60\t36\tN/A\t1+\t10
G4\t空白对照(CT)\tSUB-G4-022\t缺血性\tT3\t21\t70\t38\t22.8\t1+\t10
G4\t空白对照(CT)\tSUB-G4-023\t缺血性\tT0\t19\t61\t20\tN/A\t1+\t12
G4\t空白对照(CT)\tSUB-G4-023\t缺血性\tT1\t19\t59\t28\t>42\t1+\t12
G4\t空白对照(CT)\tSUB-G4-023\t缺血性\tT2\t19\t63\t31\tN/A\t1+\t11
G4\t空白对照(CT)\tSUB-G4-023\t缺血性\tT3\t21\t73\t38\t15.7\t1+\t11
G4\t空白对照(CT)\tSUB-G4-024\t缺血性\tT0\t24\t60\t34\t>45\t1+\t13
G4\t空白对照(CT)\tSUB-G4-024\t缺血性\tT1\t25\t58\t34\t>42\t2\t12
G4\t空白对照(CT)\tSUB-G4-024\t缺血性\tT2\t25\t56\t42\t>42\t1+\t12
G4\t空白对照(CT)\tSUB-G4-024\t缺血性\tT3\t26\t66\t44\t23.6\t1+\t12
G4\t空白对照(CT)\tSUB-G4-025\t缺血性\tT0\t19\t49\t26\tN/A\t1+\t13
G4\t空白对照(CT)\tSUB-G4-025\t缺血性\tT1\t22\t60\t31\tN/A\t1+\t11
G4\t空白对照(CT)\tSUB-G4-025\t缺血性\tT2\t22\t58\t33\tN/A\t1+\t10
G4\t空白对照(CT)\tSUB-G4-025\t缺血性\tT3\t23\t56\t37\t30.4\t1+\t10
G4\t空白对照(CT)\tSUB-G4-026\t缺血性\tT0\t22\t71\t25\tN/A\t2\t13
G4\t空白对照(CT)\tSUB-G4-026\t缺血性\tT1\t24\t69\t28\tN/A\t2\t13
G4\t空白对照(CT)\tSUB-G4-026\t缺血性\tT2\t24\t68\t34\t>42\t1+\t13
G4\t空白对照(CT)\tSUB-G4-026\t缺血性\tT3\t24\t66\t37\t36.2\t1+\t12
G4\t空白对照(CT)\tSUB-G4-027\t缺血性\tT0\t23\t52\t35\t>45\t2\t13
G4\t空白对照(CT)\tSUB-G4-027\t缺血性\tT1\t24\t59\t35\t>42\t1+\t13
G4\t空白对照(CT)\tSUB-G4-027\t缺血性\tT2\t24\t69\t35\tN/A\t1+\t11
G4\t空白对照(CT)\tSUB-G4-027\t缺血性\tT3\t24\t67\t38\t38.1\t1+\t11
G4\t空白对照(CT)\tSUB-G4-028\t缺血性\tT0\t18\t56\t20\tN/A\t1+\t12
G4\t空白对照(CT)\tSUB-G4-028\t缺血性\tT1\t21\t54\t23\tN/A\t1+\t12
G4\t空白对照(CT)\tSUB-G4-028\t缺血性\tT2\t21\t55\t33\tN/A\t1+\t12
G4\t空白对照(CT)\tSUB-G4-028\t缺血性\tT3\t25\t63\t37\t44.1\t1+\t12
G4\t空白对照(CT)\tSUB-G4-029\t缺血性\tT0\t20\t60\t29\t>45\t2\t13
G4\t空白对照(CT)\tSUB-G4-029\t缺血性\tT1\t22\t67\t34\t>42\t2\t12
G4\t空白对照(CT)\tSUB-G4-029\t缺血性\tT2\t23\t65\t34\tN/A\t1+\t12
G4\t空白对照(CT)\tSUB-G4-029\t缺血性\tT3\t23\t63\t37\t30.2\t1+\t12
G4\t空白对照(CT)\tSUB-G4-030\t缺血性\tT0\t19\t61\t20\tN/A\t1+\t12
G4\t空白对照(CT)\tSUB-G4-030\t缺血性\tT1\t19\t59\t28\t>42\t1+\t12
G4\t空白对照(CT)\tSUB-G4-030\t缺血性\tT2\t19\t63\t31\tN/A\t1+\t11
G4\t空白对照(CT)\tSUB-G4-030\t缺血性\tT3\t21\t73\t38\t15.7\t1+\t11"""

# 读取数据
df = pd.read_csv(io.StringIO(data_text), sep='\t')

# 保存完整 CSV
df.to_csv('stroke_data.csv', index=False, encoding='utf-8-sig')

# 筛选基线 (T0)
bl = df[df['时间点'] == 'T0'].copy()

# 数值列
num_cols = ['FMA_LE', 'ADL', 'BBS', 'CSS']
# TUGT 和 MAS 有 N/A 和 >42 等文本值，在基线分析里先跳过完整统计，只做计数

# 保存基线 CSV 方便 SPSS 导入
bl.to_csv('stroke_baseline.csv', index=False, encoding='utf-8-sig')

print(f"总数据量：{len(df)} 行（含 {df['时间点'].nunique()} 个时间点）")
print(f"基线(T0)数据量：{len(bl)} 行，4组各 {bl.groupby('分组').size().tolist()} 例")
print("\n文件已生成：")
print("  - stroke_data.csv (完整数据)")
print("  - stroke_baseline.csv (仅基线T0)")
print("\n" + "="*60)
print("【基线描述性统计】（T0，按分组）")
print("="*60)

for col in num_cols:
    print(f"\n>>> {col}")
    desc = bl.groupby('分组')[col].agg(['count','mean','std','min','max']).round(2)
    print(desc)
    
    # 正态性检验 (Shapiro-Wilk)，按合并样本（因为n=30不够大，分组检验可能意义有限）
    stat, p = stats.shapiro(bl[col].dropna())
    normal = p > 0.05
    print(f"    正态性检验(Shapiro-Wilk): W={stat:.3f}, p={p:.3f} → {'正态' if normal else '非正态'}")
    
    # 方差齐性 (Levene)
    groups = [group[col].dropna().values for name, group in bl.groupby('分组')]
    levene_stat, levene_p = stats.levene(*groups)
    print(f"    方差齐性检验(Levene): W={levene_stat:.3f}, p={levene_p:.3f}")
    
    # 组间比较
    if normal and levene_p > 0.05:
        f_stat, p_val = stats.f_oneway(*groups)
        print(f"    组间比较(One-way ANOVA): F={f_stat:.3f}, p={p_val:.3f}")
    else:
        h_stat, p_val = stats.kruskal(*groups)
        print(f"    组间比较(Kruskal-Wallis): H={h_stat:.3f}, p={p_val:.3f}")

# 卒中亚型（分类变量）
print("\n" + "="*60)
print("【卒中亚型分布】（T0）")
print("="*60)
ct = pd.crosstab(bl['分组'], bl['卒中亚型'])
print(ct)
chi2, p, dof, expected = stats.chi2_contingency(ct)
print(f"\n卡方检验: χ²={chi2:.3f}, p={p:.3f}, df={dof}")

# TUGT 和 MAS 基线计数（含缺失/截尾值）
print("\n" + "="*60)
print("【TUGT 基线状态】（T0，含 N/A 和截尾值）")
print("="*60)
print(bl.groupby('分组')['TUGT'].value_counts().unstack(fill_value=0))

print("\n" + "="*60)
print("【MAS 基线分布】（T0）")
print("="*60)
print(bl.groupby('分组')['MAS'].value_counts().unstack(fill_value=0))

print("\n分析完成！")
