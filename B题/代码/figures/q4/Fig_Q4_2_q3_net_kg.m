%% Fig.Q4-2  Q3 各质量参数的边际净 KG
clear; close all; clc;
here=fileparts(mfilename('fullpath')); dataDir=fullfile(here,'..','..','results','q4');
T=readtable(fullfile(dataDir,'q3_kg_action_values.csv'),'VariableNamingRule','preserve'); T=T(~strcmp(string(T.action),'STOP'),:);
names={'part_1','part_2','part_3','part_4','part_5','part_6','part_7','part_8','semi_1','semi_2','semi_3','final'};
labels={'零件1','零件2','零件3','零件4','零件5','零件6','零件7','零件8','半成品1','半成品2','半成品3','最终成品'};
fig=figure('Color','w','Name','Fig.Q4-2 Q3净KG','NumberTitle','off'); tiledlayout(fig,2,2,'TileSpacing','compact','Padding','loose'); ink=[.12 .12 .12];
priors={'uniform','jeffreys'};
for q=1:2
    R=T(strcmp(string(T.prior),priors{q}),:); [~,idx]=ismember(names,string(R.action)); R=R(idx,:);
    for g=1:2
        if g==1, sel=1:8; else, sel=9:12; end
        ax=nexttile; hold(ax,'on'); x=R.net_KG(sel); lo=R.net_KG_CI_lower(sel); hi=R.net_KG_CI_upper(sel); y=1:numel(sel);
        errorbar(ax,x,y,x-lo,hi-x,'horizontal','o','Color',[.12 .35 .58],'MarkerFaceColor',[.12 .35 .58],'LineWidth',1.0,'CapSize',5);
        xline(ax,0,'--','Color',[.78 .18 .16],'LineWidth',1.1);
        set(ax,'YTick',y,'YTickLabel',labels(sel),'YDir','reverse','Color','w','XColor',ink,'YColor',ink,'Box','off','FontName',fontNameCN(),'FontSize',9);
        xlabel(ax,'Net KG（元/件）','FontName',fontNameCN(),'Color',ink);
        if g==1, title(ax,sprintf('(%c) %s先验—零件层',char('a'+(q-1)*2),priorLabel(priors{q})),'FontName',fontNameCN(),'FontWeight','normal','Color',ink);
            xlim(ax,[min(lo)-.3 max(hi)+.3]);
        else, title(ax,sprintf('(%c) %s先验—半成品及成品',char('a'+(q-1)*2+1),priorLabel(priors{q})),'FontName',fontNameCN(),'FontWeight','normal','Color',ink);
            xlim(ax,[min(lo)-5 max(hi)+5]);
        end
        grid(ax,'on'); ax.GridAlpha=.16;
        for k=1:numel(sel)
            text(ax,hi(k),y(k),sprintf('  %.2f',x(k)),'FontName','Times New Roman','FontSize',8,'Color',ink,'VerticalAlignment','bottom');
        end
    end
end
sgtitle(fig,'演示抽样情景下问题三各质量参数的边际净信息价值（一步 KG）','FontName',fontNameCN(),'FontWeight','normal','Color',ink);
annotation(fig,'textbox',[.12 .005 .76 .02],'String','误差棒为独立确认批次给出的95%净 KG 区间；红色虚线为 KG=0，当前所有区间上界均低于0。一步 KG 结果不等同于全局序贯最优性证明。','EdgeColor','none','HorizontalAlignment','center','FontName',fontNameCN(),'FontSize',8,'Color',ink);

function out=priorLabel(p)
if strcmp(p,'uniform'), out='均匀'; else, out='Jeffreys'; end
end

function name=fontNameCN()
fonts=listfonts; candidates={'Noto Serif CJK SC','Source Han Serif SC','SimSun','Songti SC','Microsoft YaHei'}; name='DejaVu Serif';
for i=1:numel(candidates), if any(strcmpi(fonts,candidates{i})), name=candidates{i}; return; end, end
end
