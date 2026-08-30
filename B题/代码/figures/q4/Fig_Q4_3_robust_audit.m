%% Fig.Q4-3  Bayesian 终止策略与数值稳健审计比较
clear; close all; clc;
here=fileparts(mfilename('fullpath')); dataDir=fullfile(here,'..','..','results','q4');
T=readtable(fullfile(dataDir,'robust_audit.csv'),'VariableNamingRule','preserve'); ink=[.12 .12 .12];
fig=figure('Color','w','Name','Fig.Q4-3 稳健审计','NumberTitle','off'); tiledlayout(fig,2,2,'TileSpacing','compact','Padding','compact');
for q=1:2
    domain={'q2','q3'}; U=T(strcmp(string(T.domain),domain{q}),:);
    for z=1:2
        cov=[90 95]; R=U(U.coverage==cov(z),:); ax=nexttile; hold(ax,'on');
        if q==1
            x=1:height(R); names=compose('情形%d',R.('case')); vals=[R.bayesian_policy_worst_profit R.robust_policy_worst_profit];
        else
            x=1; names={'Q3'}; vals=[R.bayesian_policy_worst_profit R.robust_policy_worst_profit];
        end
        bar(ax,x,vals,'grouped');
        set(ax,'Color','w','XColor',ink,'YColor',ink,'Box','off','FontName',fontNameCN(),'FontSize',9,'XTick',x,'XTickLabel',names);
        ylabel(ax,'最坏利润（元/件）','FontName',fontNameCN(),'Color',ink);
        title(ax,sprintf('(%c) %s，%d%% 联合集合',char('a'+(q-1)*2+z-1),upper(domain{q}),cov(z)), ...
            'FontName',fontNameCN(),'FontWeight','normal','Color',ink);
        grid(ax,'on'); ax.GridAlpha=.16;
        for i=1:height(R)
            if string(R.bayesian_policy(i)) ~= string(R.robust_policy(i))
                text(ax,x(i),max(vals(i,:))+0.05*max(abs(vals(:))),sprintf('策略切换：%s → %s', ...
                    char(string(R.bayesian_policy(i))),char(string(R.robust_policy(i)))), ...
                    'HorizontalAlignment','center','FontName','Times New Roman','FontSize',8,'Color',ink);
            end
        end
        if q==1, legend(ax,{'Bayesian 终止策略','数值稳健策略'},'Location','best','FontName',fontNameCN(),'Box','off','TextColor',ink,'Color','w'); end
    end
end
sgtitle(fig,'演示抽样情景下 Bayesian 与数值稳健策略的最坏利润比较','FontName',fontNameCN(),'FontWeight','normal','Color',ink);
annotation(fig,'textbox',[.12 .005 .76 .035],'String','稳健审计状态为 ROBUST_NUMERICAL；结果基于矩形联合区间端点数值评价，不表示严格认证的全局稳健最优。','EdgeColor','none','HorizontalAlignment','center','FontName',fontNameCN(),'FontSize',9,'Color',ink);

function name=fontNameCN()
fonts=listfonts; candidates={'Noto Serif CJK SC','Source Han Serif SC','SimSun','Songti SC','Microsoft YaHei'}; name='DejaVu Serif';
for i=1:numel(candidates), if any(strcmpi(fonts,candidates{i})), name=candidates{i}; return; end, end
end
