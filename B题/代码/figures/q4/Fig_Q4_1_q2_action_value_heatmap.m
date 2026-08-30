%% Fig.Q4-1  Q2 初始动作价值差热力图
clear; close all; clc;
here=fileparts(mfilename('fullpath')); dataDir=fullfile(here,'..','..','results','q4');
T=readtable(fullfile(dataDir,'q2_voi_policy_summary.csv'),'VariableNamingRule','preserve');
rows=height(T); labels=cell(rows,1); delta=nan(rows,4); actionNames={'STOP','检测 p_1','检测 p_2','检测 p_f'};
for i=1:rows
    labels{i}=sprintf('情形%d-%s',T.('case')(i),char(string(T.prior(i))));
    obj=jsondecode(char(string(T.initial_action_values(i))));
    stop=obj.STOP; delta(i,:)=[0,obj.p1-stop,obj.p2-stop,obj.pf-stop];
end
fig=figure('Color','w','Name','Fig.Q4-1 Q2动作价值','NumberTitle','off');
ax=axes(fig,'Color','w','XColor',[.12 .12 .12],'YColor',[.12 .12 .12]); imagesc(ax,delta); set(ax,'YDir','normal');
lim=max(abs(delta(:))); colormap(ax,[linspace(.18,1,128)' linspace(.40,1,128)' ones(128,1); ones(128,1) linspace(1,.55,128)' linspace(1,.45,128)']); caxis(ax,[-lim lim]);
set(ax,'XTick',1:4,'XTickLabel',actionNames,'YTick',1:rows,'YTickLabel',labels,'FontName',fontNameCN(),'FontSize',9,'Box','off');
xlabel(ax,'初始动作','FontName',fontNameCN(),'Color',[.12 .12 .12]); ylabel(ax,'情形与先验','FontName',fontNameCN(),'Color',[.12 .12 .12]);
title(ax,'演示抽样情景下问题二追加抽样动作价值差','FontName',fontNameCN(),'FontWeight','normal','Color',[.12 .12 .12]);
cb=colorbar(ax); cb.Label.String='\\Delta Q_a=Q_a-G(s)（元/件）'; cb.FontName='Times New Roman'; cb.Color=[.12 .12 .12];
for i=1:rows, for j=1:4
    text(ax,j,i,sprintf('%.3f',delta(i,j)),'HorizontalAlignment','center','FontName','Times New Roman','FontSize',8,'Color',pickText(delta(i,j),lim),'FontWeight','bold');
end, end
annotation(fig,'textbox',[.18 .005 .64 .035],'String','STOP 的价值差定义为 0；负值表示追加检测的期望净价值低于立即停止。','EdgeColor','none','HorizontalAlignment','center','FontName',fontNameCN(),'FontSize',9,'Color',[.12 .12 .12]);

function c=pickText(v,lim), if abs(v)>0.55*lim, c=[1 1 1]; else, c=[.1 .1 .1]; end, end
function name=fontNameCN()
fonts=listfonts; candidates={'Noto Serif CJK SC','Source Han Serif SC','SimSun','Songti SC','Microsoft YaHei'}; name='DejaVu Serif';
for i=1:numel(candidates), if any(strcmpi(fonts,candidates{i})), name=candidates{i}; return; end, end
end
