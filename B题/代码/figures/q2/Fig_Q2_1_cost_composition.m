%% Fig.Q2-1  问题二最优固定策略的期望成本构成
% 直接读取 results/q2 的最终结果；运行本脚本只在 MATLAB 中显示图形。
clear; close all; clc;

here = fileparts(mfilename('fullpath'));
dataDir = fullfile(here, '..', '..', 'results', 'q2');
best = readtable(fullfile(dataDir, 'best_policies.csv'), 'VariableNamingRule', 'preserve');
allp = readtable(fullfile(dataDir, 'all_policies.csv'), 'VariableNamingRule', 'preserve');

% 情形 3 的并列最优从全策略结果恢复，不能只读 best_policies 单行。
selected = allp([],:); labels = {};
for c = 1:6
    rows = allp(allp.('case') == c, :);
    minCost = min(rows.('expected_total_cost'));
    rows = rows(abs(rows.('expected_total_cost') - minCost) <= 1e-9, :);
    if c == 3
        rows = sortrows(rows, {'x1','x2','y','z'});
        for k = 1:height(rows)
            selected = [selected; rows(k,:)]; %#ok<AGROW>
            labels{end+1} = sprintf('情形3-%s', char('A' + k - 1)); %#ok<AGROW>
        end
    else
        selected = [selected; best(best.('case') == c,:)]; %#ok<AGROW>
        labels{end+1} = sprintf('情形%d', c); %#ok<AGROW>
    end
end

costNames = {'采购','零件检测','装配','成品检测','拆解','调换损失'};
% 采购与零件检测分别合并两种零件，拆解与调换保持独立。
costs = [selected.('cost_purchase_1') + selected.('cost_purchase_2'), ...
    selected.('cost_inspection_1') + selected.('cost_inspection_2'), ...
    selected.('cost_assembly'), selected.('cost_product_inspection'), ...
    selected.('cost_disassembly'), selected.('cost_replacement_loss')];
profits = selected.('expected_profit');

fig = figure('Color','w', 'Name','Fig.Q2-1 成本构成', 'NumberTitle','off');
ax = axes(fig, 'Color','w', 'XColor',[0.12 0.12 0.12], 'YColor',[0.12 0.12 0.12]); hold(ax, 'on');
colors = [0.12 0.35 0.58; 0.85 0.47 0.18; 0.25 0.55 0.35; ...
          0.48 0.38 0.68; 0.55 0.42 0.25; 0.40 0.40 0.40];
b = bar(ax, costs, 'stacked', 'BarWidth', 0.72);
for j = 1:numel(b)
    b(j).FaceColor = colors(j,:); b(j).EdgeColor = [0.15 0.15 0.15];
    b(j).LineWidth = 0.35;
end
set(ax, 'XTick', 1:numel(labels), 'XTickLabel', labels, 'FontName', fontNameCN(), ...
    'FontSize', 10, 'LineWidth', 0.8, 'Box', 'off');
xlabel(ax, '生产情形（最终成功交付一件合格品）', 'FontName', fontNameCN(), 'Color',[0.12 0.12 0.12]);
ylabel(ax, '期望成本（元/件）', 'FontName', fontNameCN(), 'Color',[0.12 0.12 0.12]);
title(ax, '问题二最优固定策略的期望成本构成', 'FontName', fontNameCN(), 'FontWeight','normal', 'Color',[0.12 0.12 0.12]);
legend(ax, costNames, 'Location','northoutside', 'Orientation','horizontal', ...
    'FontName', fontNameCN(), 'Box','off', 'TextColor',[0.12 0.12 0.12], 'Color','w');
grid(ax, 'on'); ax.GridAlpha = 0.16; ax.Layer = 'top';
totals = sum(costs, 2);
for i = 1:numel(labels)
    text(ax, i, totals(i) + 0.7, sprintf('\\Pi=%.3f', profits(i)), ...
        'HorizontalAlignment','center', 'FontName','Times New Roman', 'FontSize',9, 'Color',[0.12 0.12 0.12]);
end
annotation(fig, 'textbox', [0.12 0.005 0.76 0.035], 'String', ...
    '情形3-A/3-B 为并列最优：分别支付成品检测成本或承担调换损失。', ...
    'EdgeColor','none', 'HorizontalAlignment','center', 'FontName',fontNameCN(), 'FontSize',9, 'Color',[0.12 0.12 0.12]);

function name = fontNameCN()
fonts = listfonts;
candidates = {'Noto Serif CJK SC','Source Han Serif SC','SimSun','Songti SC','Microsoft YaHei'};
name = 'DejaVu Serif';
for i = 1:numel(candidates)
    if any(strcmpi(fonts, candidates{i})), name = candidates{i}; return; end
end
end
